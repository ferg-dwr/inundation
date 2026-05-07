"""Fremont Weir stage height data from CDEC.

This module provides access to Fremont Weir hourly stage height data
from the California Data Exchange Center (CDEC).
"""

import io
from datetime import datetime

import pandas as pd
import requests

from .cache import (
    add_to_index,
    cache_exists,
    get_cache_file,
    make_cache_key,
    matches_cache_request,
)


def _get_cdec_url(
    station_id: str = "FRE",
    sensor_num: int = 1,
    duration: str = "H",
    start: str = "1940-01-01",
    end: str | None = None,
) -> str:
    """Build the CDEC API URL for a given station and date range.

    Parameters
    ----------
    station_id : str, optional
        CDEC station ID. Default "FRE" (Fremont Weir).
    sensor_num : int, optional
        Sensor number. Default 1 (stage height).
    duration : str, optional
        Duration code. Default "H" (hourly).
    start : str, optional
        Start date in YYYY-MM-DD format.
    end : str, optional
        End date in YYYY-MM-DD format. Default: today.

    Returns
    -------
    str
        Full CDEC API URL.
    """
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    return (
        "https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet"
        f"?Stations={station_id}"
        f"&SensorNums={sensor_num}"
        f"&dur_code={duration}"
        f"&Start={start}"
        f"&End={end}"
    )


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names: lowercase, replace spaces/hyphens with underscores.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with messy column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with cleaned column names.
    """
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
    return df


def get_fre(
    station_id: str = "FRE",
    start: str = "1940-01-01",
    end: str | None = None,
    use_cache: bool = True,
    refresh: bool = False,
) -> pd.DataFrame:
    """Download Fremont Weir stage height data from CDEC.

    Caching behavior:

    - ``use_cache=True`` (default): Read from cache if a matching entry exists,
      otherwise download. Save successful downloads to cache.

    - ``use_cache=False``: Disable BOTH reading and writing to cache.
      Use this for one-off queries that should not affect cache state
      (e.g., testing, exploring, or full reproducibility).

    - ``refresh=True``: Force a fresh download even if cache exists.
      Still writes the new data to cache for future use.

    Parameters
    ----------
    station_id : str, optional
        CDEC station ID. Default "FRE" (Fremont Weir).
    start : str, optional
        Start date in YYYY-MM-DD format. Default "1940-01-01".
    end : str, optional
        End date in YYYY-MM-DD format. Default: today's date.
    use_cache : bool, default True
        If True, read from and write to cache.
        If False, disables cache reading AND writing entirely.
    refresh : bool, default False
        If True, force fresh download even if cache exists.
        Still writes to cache (unless use_cache=False).

    Returns
    -------
    pd.DataFrame
        DataFrame with hourly stage height data.

    Examples
    --------
    Standard usage (uses cache):

    >>> fre = get_fre()

    Get specific date range:

    >>> fre = get_fre(start="2020-01-01", end="2020-12-31")

    Force fresh download but keep caching:

    >>> fre = get_fre(refresh=True)

    Run without touching cache (testing, exploration):

    >>> fre = get_fre(use_cache=False)

    Notes
    -----
    Cache files are named using request parameters for clarity:
    ``fre_FRE_2020-01-01_2020-12-31.csv``

    To inspect cached files, use :func:`inundation.cache.show_cache`.
    To clear cache, use :func:`inundation.cache.clear_cache`.
    """
    # Default end to today if not provided
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    # Build cache parameters (these affect the result)
    cache_params = {
        "station_id": station_id,
        "start": start,
        "end": end,
    }

    # Generate cache filename based on parameters
    cache_filename = make_cache_key("fre", cache_params)

    # CACHE READ: Try to read from cache if enabled and not refreshing
    if use_cache and not refresh:
        if cache_exists(cache_filename) and matches_cache_request(cache_filename, cache_params):
            print(f"Reading Fremont Weir data from cache: {cache_filename}")
            df = pd.read_csv(get_cache_file(cache_filename))
            df["datetime"] = pd.to_datetime(df["datetime"])
            return df

    # DOWNLOAD: Either no cache, or refresh requested, or cache disabled
    print("Downloading Fremont Weir data from CDEC...")
    url = _get_cdec_url(station_id=station_id, start=start, end=end)

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download data from CDEC: {e}") from e

    # Parse CSV
    fre = pd.read_csv(io.StringIO(response.text))
    fre = _clean_column_names(fre)

    # Drop unnecessary columns if they exist
    cols_to_drop = ["obs_date", "data_flag"]
    fre = fre.drop(columns=[c for c in cols_to_drop if c in fre.columns])

    # Rename date_time to datetime
    if "date_time" in fre.columns:
        fre = fre.rename(columns={"date_time": "datetime"})

    # Convert types
    fre["datetime"] = pd.to_datetime(fre["datetime"], errors="coerce")
    fre["value"] = pd.to_numeric(fre["value"], errors="coerce")

    # CACHE WRITE: Save to cache if enabled
    if use_cache:
        cache_path = get_cache_file(cache_filename)
        fre.to_csv(cache_path, index=False)

        # Add to cache index with metadata
        add_to_index(
            filename=cache_filename,
            params=cache_params,
            source_url=url,
            row_count=len(fre),
        )
        print(f"Cached to: {cache_filename}")

    return fre
