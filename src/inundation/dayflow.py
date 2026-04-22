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

from .cache import cache_exists, get_cache_file


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


def get_dayflow(use_cache: bool = True) -> pd.DataFrame:
    """Download Dayflow data for Sacramento River and Yolo Bypass.

    Downloads daily flow data from the California Natural Resources Agency.
    Data includes flows for the Sacramento River (SAC) and Yolo Bypass (YOLO).

    Data is retrieved from the CNRA's JSON API, which returns multiple CSV files
    that are parsed, combined, and cached locally.

    Parameters
    ----------
    use_cache : bool, default True
        If True, read from cache if available. If False, always download.

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
    >>> dayflow = get_dayflow()
    >>> print(dayflow.head())

    Download new data without cache:

    >>> dayflow = get_dayflow(use_cache=False)

    Notes
    -----
    Data is cached locally. To view cached files, use `inundation.cache.show_cache()`.
    To clear the cache, use `inundation.cache.clear_cache()`.

    The dayflow dataset begins October 1, 1955.

    See Also
    --------
    get_fre : Download Fremont Weir stage height data
    calc_inundation : Calculate inundation duration

    References
    ----------
    - Dayflow: https://data.cnra.ca.gov/dataset/dayflow
    """
    cache_file = get_cache_file("dayflow.csv")

    # Try to read from cache if available
    if use_cache and cache_exists("dayflow.csv"):
        print("Reading dayflow data from cache. To download new data, use use_cache=False.")
        dayflow = pd.read_csv(cache_file)
        dayflow["date"] = pd.to_datetime(dayflow["date"])
        return dayflow

    # Download metadata from CNRA JSON API
    print("Downloading dayflow data from CNRA...")
    try:
        response = requests.get(
            "https://data.cnra.ca.gov/dataset/06ee2016-b138-47d7-9e85-f46fae674536.jsonld",
            timeout=30,
        )
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

    # Cache the data
    dayflow.to_csv(cache_file, index=False)
    print(f"Data cached to {cache_file}")

    return dayflow


__all__ = ["get_dayflow"]
