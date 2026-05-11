"""Download and process California Dayflow data.

This module downloads daily flow data for the Sacramento River and Yolo Bypass
from the California Natural Resources Agency (CNRA).

Dayflow data shows modeled daily flows of water through the Sacramento-San
Joaquin Delta system.

Data source: https://data.cnra.ca.gov/dataset/dayflow
"""

import io
import json

import pandas as pd
import requests

from .cache import (
    add_to_index,
    cache_exists,
    get_cache_file,
    matches_cache_request,
)


def _get_csv_urls_from_metadata(metadata: dict) -> list[str]:
    """Extract CSV download URLs from CNRA metadata.

    Parameters
    ----------
    metadata : dict
        JSON metadata from CNRA API

    Returns
    -------
    list[str]
        List of CSV URLs containing 'results'

    Raises
    ------
    RuntimeError
        If unable to extract URLs or none found
    """
    try:
        graph = metadata.get("@graph", [])
        urls: list[str] = []

        for item in graph:
            if item.get("dct:format") == "CSV":
                access_url = item.get("dcat:accessURL", {})
                if isinstance(access_url, dict):
                    url = access_url.get("@id")
                else:
                    url = access_url
                if url and "results" in url:
                    urls.append(url)
    except (KeyError, TypeError) as e:
        raise RuntimeError(f"Failed to extract CSV URLs from metadata: {e}") from e

    if not urls:
        raise RuntimeError("No CSV download URLs found in CNRA metadata")

    return urls


def _download_and_parse_csvs(urls: list[str]) -> list[pd.DataFrame]:
    """Download and parse all CSV files from URLs.

    Parameters
    ----------
    urls : list[str]
        List of CSV file URLs

    Returns
    -------
    list[pd.DataFrame]
        List of parsed dataframes

    Raises
    ------
    RuntimeError
        If all downloads fail
    """
    dataframes: list[pd.DataFrame] = []

    for url in urls:
        try:
            csv_response = requests.get(url, timeout=30)
            csv_response.raise_for_status()
            df = pd.read_csv(io.StringIO(csv_response.text))

            # Select only Date, SAC, YOLO columns if they exist
            cols_to_keep = [col for col in ["Date", "SAC", "YOLO"] if col in df.columns]
            if cols_to_keep:
                df = df[cols_to_keep]
                # Handle missing YOLO column
                if "YOLO" not in df.columns:
                    df["YOLO"] = None
                dataframes.append(df)
        except requests.RequestException as e:
            print(f"Warning: Failed to download {url}: {e}")
            continue
        except pd.errors.ParserError as e:
            print(f"Warning: Failed to parse {url}: {e}")
            continue

    if not dataframes:
        raise RuntimeError("Failed to download any dayflow data from CNRA")

    return dataframes


def _process_dayflow_data(dayflow: pd.DataFrame) -> pd.DataFrame:
    """Process and clean dayflow dataframe.

    Parameters
    ----------
    dayflow : pd.DataFrame
        Raw concatenated dayflow data

    Returns
    -------
    pd.DataFrame
        Cleaned and sorted dataframe
    """
    # Clean column names and convert types
    dayflow.columns = dayflow.columns.str.lower()
    dayflow["date"] = pd.to_datetime(dayflow["date"], errors="coerce")
    dayflow["sac"] = pd.to_numeric(dayflow["sac"], errors="coerce")
    dayflow["yolo"] = pd.to_numeric(dayflow["yolo"], errors="coerce")

    # Remove duplicates
    dayflow = dayflow.drop_duplicates().reset_index(drop=True)

    # Sort by date
    dayflow = dayflow.sort_values("date").reset_index(drop=True)

    return dayflow


# Cache configuration
DAYFLOW_CACHE_FILE = "dayflow.csv"
DAYFLOW_METADATA_URL = (
    "https://data.cnra.ca.gov/dataset/06ee2016-b138-47d7-9e85-f46fae674536.jsonld"
)


def get_dayflow(use_cache: bool = True, refresh: bool = False) -> pd.DataFrame:
    """Download Dayflow data for Sacramento River and Yolo Bypass.

    Downloads daily flow data from the California Natural Resources Agency.
    Data includes flows for the Sacramento River (SAC) and Yolo Bypass (YOLO).

    Caching behavior:

    - ``use_cache=True`` (default): Read from cache if available, otherwise
      download. Save successful downloads to cache.

    - ``use_cache=False``: Disable BOTH reading and writing to cache.
      Use this for one-off queries that should not affect cache state
      (e.g., testing, exploring, or full reproducibility).

    - ``refresh=True``: Force a fresh download even if cache exists.
      Still writes the new data to cache for future use.

    Parameters
    ----------
    use_cache : bool, default True
        If True, read from and write to cache.
        If False, disables cache reading AND writing entirely.
    refresh : bool, default False
        If True, force fresh download even if cache exists.
        Still writes to cache (unless use_cache=False).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - date : datetime64[ns]
            Date of flow measurement
        - sac : float
            Sacramento River flow (cubic feet per day)
        - yolo : float
            Yolo Bypass flow (cubic feet per day)

    Examples
    --------
    Standard usage (uses cache):

    >>> dayflow = get_dayflow()

    Force fresh download but keep caching:

    >>> dayflow = get_dayflow(refresh=True)

    Run without touching cache (testing, exploration):

    >>> dayflow = get_dayflow(use_cache=False)

    Notes
    -----
    The dayflow dataset begins October 1, 1929.

    To inspect cached files, use :func:`inundation.cache.show_cache`.
    To clear cache, use :func:`inundation.cache.clear_cache`.

    See Also
    --------
    get_fre : Download Fremont Weir stage height data
    calc_inundation : Calculate inundation duration

    References
    ----------
    - Dayflow: https://data.cnra.ca.gov/dataset/dayflow
    """
    # Cache parameters (dayflow has no request params - always full dataset)
    cache_params: dict[str, str] = {}

    # CACHE READ: Try to read from cache if enabled and not refreshing
    if use_cache and not refresh:
        if cache_exists(DAYFLOW_CACHE_FILE):
            # Verify cache matches request (always matches for dayflow since no params)
            if matches_cache_request(DAYFLOW_CACHE_FILE, cache_params):
                print(f"Reading dayflow data from cache: {DAYFLOW_CACHE_FILE}")
                dayflow = pd.read_csv(get_cache_file(DAYFLOW_CACHE_FILE))
                dayflow["date"] = pd.to_datetime(dayflow["date"])
                return dayflow

    # DOWNLOAD: Either no cache, or refresh requested, or cache disabled
    print("Downloading dayflow data from CNRA...")
    try:
        response = requests.get(DAYFLOW_METADATA_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download dayflow metadata from CNRA: {e}") from e

    try:
        metadata = response.json()
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse dayflow metadata JSON: {e}") from e

    # Extract CSV URLs and download data
    urls = _get_csv_urls_from_metadata(metadata)
    dataframes = _download_and_parse_csvs(urls)

    # Combine all dataframes
    dayflow = pd.concat(dataframes, ignore_index=True)

    # Process and clean
    dayflow = _process_dayflow_data(dayflow)

    # CACHE WRITE: Save to cache if enabled
    if use_cache:
        cache_path = get_cache_file(DAYFLOW_CACHE_FILE)
        dayflow.to_csv(cache_path, index=False)

        # Add to cache index with metadata
        add_to_index(
            filename=DAYFLOW_CACHE_FILE,
            params=cache_params,
            source_url=DAYFLOW_METADATA_URL,
            row_count=len(dayflow),
        )
        print(f"Cached to: {DAYFLOW_CACHE_FILE}")

    return dayflow


__all__ = ["get_dayflow"]
