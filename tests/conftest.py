"""Pytest configuration and shared fixtures."""

import io
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_fre_csv() -> str:
    """Provide sample Fremont Weir CSV data.

    Returns
    -------
    str
        Sample CSV data in CDEC format.
    """
    return """Station ID,Sensor Number,Dur Code,Date Time,Obs Date,Data Flag,Value
FRE,1,H,2020-01-01 00:00,2020-01-01,0,30.5
FRE,1,H,2020-01-01 01:00,2020-01-01,0,31.2
FRE,1,H,2020-01-01 02:00,2020-01-01,0,---
FRE,1,H,2020-01-01 03:00,2020-01-01,0,32.1
FRE,1,H,2020-01-01 04:00,2020-01-01,0,32.5"""


@pytest.fixture
def sample_fre_dataframe() -> pd.DataFrame:
    """Provide sample Fremont Weir data as DataFrame.

    Returns
    -------
    pd.DataFrame
        Sample FRE data with cleaned columns and proper dtypes.
    """
    return pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2020-01-01 00:00",
                    "2020-01-01 01:00",
                    "2020-01-01 02:00",
                    "2020-01-01 03:00",
                    "2020-01-01 04:00",
                ]
            ),
            "value": [30.5, 31.2, float("nan"), 32.1, 32.5],
            "station_id": ["FRE"] * 5,
            "sensor_number": [1] * 5,
            "duration": ["H"] * 5,
        }
    )


@pytest.fixture
def sample_dayflow_csv() -> str:
    """Provide sample Dayflow CSV data.

    Returns
    -------
    str
        Sample CSV data in Dayflow format.
    """
    return """Date,SAC,YOLO
1955-10-01,1234.5,567.8
1955-10-02,1250.3,580.1
1955-10-03,1200.0,545.3
1955-10-04,1180.5,530.2
1955-10-05,1150.0,515.0"""


@pytest.fixture
def sample_dayflow_dataframe() -> pd.DataFrame:
    """Provide sample Dayflow data as DataFrame.

    Returns
    -------
    pd.DataFrame
        Sample dayflow data with proper dtypes.
    """
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "1955-10-01",
                    "1955-10-02",
                    "1955-10-03",
                    "1955-10-04",
                    "1955-10-05",
                ]
            ),
            "sac": [1234.5, 1250.3, 1200.0, 1180.5, 1150.0],
            "yolo": [567.8, 580.1, 545.3, 530.2, 515.0],
        }
    )


@pytest.fixture
def tmp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory.

    Parameters
    ----------
    tmp_path : Path
        Pytest temporary directory fixture.

    Returns
    -------
    Path
        Path to temporary cache directory.
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def stringio_csv(sample_fre_csv: str) -> io.StringIO:
    """Provide CSV data as StringIO object.

    Parameters
    ----------
    sample_fre_csv : str
        Sample CSV data.

    Returns
    -------
    io.StringIO
        CSV data as StringIO for testing pandas.read_csv.
    """
    return io.StringIO(sample_fre_csv)
