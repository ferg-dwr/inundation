"""Download and process Fremont Weir Sacramento River stage height data.

This module downloads hourly stage height measurements from the CDEC
(California Data Exchange Center) for the Fremont Weir station (FRE).

The Fremont Weir marks the point where water spills from the Sacramento
River into the Yolo Bypass during high flow events.

Data source: https://cdec.water.ca.gov/
"""

import io
from datetime import datetime

import pandas as pd
import requests

from .cache import cache_exists, get_cache_file


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names to snake_case.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with original column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with cleaned column names in snake_case.
    """
    # Convert to lowercase and replace spaces/hyphens with underscores
    df.columns = (
        df.columns.str.lower().str.replace(" ", "_", regex=False).str.replace("-", "_", regex=False)
    )
    return df


def _get_cdec_url(
    station_id: str = "FRE",
    start: str = "1940-01-01",
    end: str | None = None,
) -> str:
    """Build CDEC data download URL.

    Parameters
    ----------
    station_id : str, default "FRE"
        Station identifier (see https://info.water.ca.gov/staMeta.html).
    start : str, default "1940-01-01"
        Start date in YYYY-MM-DD format.
    end : str, optional
        End date in YYYY-MM-DD format. If None, uses today's date.

    Returns
    -------
    str
        URL for CDEC CSV download servlet.
    """
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    base_url = "http://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet"
    params = {
        "Stations": station_id,
        "SensorNums": 1,  # Sensor 1 = Stage
        "dur_code": "H",  # H = Hourly
        "Start": start,
        "End": end,
    }

    # Build URL with query parameters
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"


def get_fre(
    station_id: str = "FRE",
    start: str = "1940-01-01",
    end: str | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Download Fremont Weir Sacramento River stage height data.

    Downloads hourly stage height measurements from the CDEC for the
    Fremont Weir (FRE) station. Data is cached locally to reduce
    download time on subsequent calls.

    The Fremont Weir is the point where the Sacramento River spills
    into the Yolo Bypass during high water conditions.

    Parameters
    ----------
    station_id : str, default "FRE"
        Station identifier. See https://info.water.ca.gov/staMeta.html
        for available stations.
    start : str, default "1940-01-01"
        Start date in YYYY-MM-DD format.
    end : str, optional
        End date in YYYY-MM-DD format. If None, uses today's date.
    use_cache : bool, default True
        If True, read from cache if available. If False, always download.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - datetime : datetime64[ns]
            Date and time of measurement
        - value : float
            Stage height in feet. NaN for missing values (e.g., "---").
        - station_id : str
            Station identifier (e.g., "FRE")
        - sensor_number : str
            Sensor number
        - duration : str
            Data duration code (e.g., "H" for hourly)

    Examples
    --------
    >>> fre = get_fre()
    >>> print(fre.head())

    Download new data without cache:

    >>> fre = get_fre(use_cache=False)

    Download data for a specific date range:

    >>> fre = get_fre(start="2020-01-01", end="2020-12-31")

    Notes
    -----
    Data is cached in the user's system cache directory. To view cached
    files, use `inundation.cache.show_cache()`. To clear the cache, use
    `inundation.cache.clear_cache()`.

    See Also
    --------
    get_dayflow : Download dayflow data
    calc_inundation : Calculate inundation duration

    References
    ----------
    - CDEC Portal: https://cdec.water.ca.gov/
    - Station metadata: https://info.water.ca.gov/staMeta.html
    """
    cache_file = get_cache_file("fre.csv")

    # Try to read from cache if available
    if use_cache and cache_exists("fre.csv"):
        print("Reading Fremont weir data from cache. To download new data, use use_cache=False.")
        fre = pd.read_csv(cache_file)
        # Ensure datetime column is parsed as datetime
        fre["datetime"] = pd.to_datetime(fre["datetime"])
        return fre

    # Build URL and download data
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")

    url = _get_cdec_url(station_id=station_id, start=start, end=end)

    print(f"Downloading Fremont weir data from {start} to {end}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download data from CDEC: {e}") from e

    # Parse CSV from response
    try:
        fre = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        raise RuntimeError(f"Failed to parse CDEC response: {e}") from e

    # Clean column names
    fre = _clean_column_names(fre)

    # Remove unwanted columns (obs_date, data_flag)
    columns_to_drop = [col for col in ["obs_date", "data_flag"] if col in fre.columns]
    fre = fre.drop(columns=columns_to_drop)

    # Rename date_time to datetime
    if "date_time" in fre.columns:
        fre = fre.rename(columns={"date_time": "datetime"})

    # Parse datetime and coerce value to numeric
    fre["datetime"] = pd.to_datetime(fre["datetime"], errors="coerce")
    fre["value"] = pd.to_numeric(fre["value"], errors="coerce")

    # Sort by datetime
    fre = fre.sort_values("datetime").reset_index(drop=True)

    # Cache the data
    fre.to_csv(cache_file, index=False)
    print(f"Data cached to {cache_file}")

    return fre


__all__ = ["get_fre"]
