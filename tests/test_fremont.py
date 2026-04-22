"""Tests for the fremont module."""

import io
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from inundation.fremont import _clean_column_names, _get_cdec_url, get_fre


class TestCleanColumnNames:
    """Test the _clean_column_names function."""

    def test_lowercase_conversion(self) -> None:
        """Test that column names are converted to lowercase."""
        df = pd.DataFrame({"DATE_TIME": [1, 2], "VALUE": [3, 4]})
        result = _clean_column_names(df)
        assert list(result.columns) == ["date_time", "value"]

    def test_space_replacement(self) -> None:
        """Test that spaces in column names are replaced with underscores."""
        df = pd.DataFrame({"Date Time": [1, 2], "Station ID": [3, 4]})
        result = _clean_column_names(df)
        assert list(result.columns) == ["date_time", "station_id"]

    def test_hyphen_replacement(self) -> None:
        """Test that hyphens in column names are replaced with underscores."""
        df = pd.DataFrame({"Date-Time": [1, 2], "Station-ID": [3, 4]})
        result = _clean_column_names(df)
        assert list(result.columns) == ["date_time", "station_id"]

    def test_multiple_transformations(self) -> None:
        """Test multiple transformations on a single dataframe."""
        df = pd.DataFrame({"DATE TIME": [1, 2], "STATION-ID": [3, 4]})
        result = _clean_column_names(df)
        assert list(result.columns) == ["date_time", "station_id"]


class TestGetCdecUrl:
    """Test the _get_cdec_url function."""

    def test_default_parameters(self) -> None:
        """Test URL construction with default parameters."""
        url = _get_cdec_url()
        assert "Stations=FRE" in url
        assert "SensorNums=1" in url
        assert "dur_code=H" in url
        assert "Start=1940-01-01" in url

    def test_custom_station_id(self) -> None:
        """Test URL with custom station ID."""
        url = _get_cdec_url(station_id="ABC")
        assert "Stations=ABC" in url
        assert "Stations=FRE" not in url

    def test_custom_start_date(self) -> None:
        """Test URL with custom start date."""
        url = _get_cdec_url(start="2020-01-01")
        assert "Start=2020-01-01" in url

    def test_custom_end_date(self) -> None:
        """Test URL with custom end date."""
        url = _get_cdec_url(end="2020-12-31")
        assert "End=2020-12-31" in url

    def test_url_contains_base(self) -> None:
        """Test that URL contains CDEC base URL."""
        url = _get_cdec_url()
        assert "cdec.water.ca.gov" in url
        assert "CSVDataServlet" in url


class TestGetFre:
    """Test the get_fre function."""

    def test_download_success(self) -> None:
        """Test successful data download."""
        mock_csv = """Station ID,Sensor Number,Dur Code,Date Time,Data Flag,Value
FRE,1,H,2020-01-01 00:00,0,30.5
FRE,1,H,2020-01-01 01:00,0,31.2
FRE,1,H,2020-01-01 02:00,0,---"""

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with patch("inundation.fremont.pd.DataFrame.to_csv"):
                    result = get_fre(use_cache=False)

        assert isinstance(result, pd.DataFrame)
        assert "datetime" in result.columns
        assert "value" in result.columns
        assert len(result) == 3

    def test_value_coercion_to_numeric(self) -> None:
        """Test that value column is converted to numeric."""
        mock_csv = """Station ID,Sensor Number,Dur Code,Date Time,Data Flag,Value
FRE,1,H,2020-01-01 00:00,0,30.5
FRE,1,H,2020-01-01 01:00,0,---
FRE,1,H,2020-01-01 02:00,0,31.2"""

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with patch("inundation.fremont.pd.DataFrame.to_csv"):
                    result = get_fre(use_cache=False)

        assert result["value"].dtype in ["float64", "Float64"]
        assert pd.isna(result.loc[1, "value"])  # --- becomes NaN
        assert result.loc[0, "value"] == 30.5

    def test_datetime_parsing(self) -> None:
        """Test that datetime column is properly parsed."""
        mock_csv = """Station ID,Sensor Number,Dur Code,Date Time,Data Flag,Value
FRE,1,H,2020-01-01 00:00,0,30.5
FRE,1,H,2020-01-01 01:00,0,31.2"""

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with patch("inundation.fremont.pd.DataFrame.to_csv"):
                    result = get_fre(use_cache=False)

        assert pd.api.types.is_datetime64_any_dtype(result["datetime"])

    def test_columns_removed(self) -> None:
        """Test that obs_date and data_flag columns are removed."""
        mock_csv = """Station ID,Sensor Number,Dur Code,Date Time,Obs Date,Data Flag,Value
FRE,1,H,2020-01-01 00:00,2020-01-01,0,30.5"""

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with patch("inundation.fremont.pd.DataFrame.to_csv"):
                    result = get_fre(use_cache=False)

        assert "obs_date" not in result.columns
        assert "data_flag" not in result.columns

    def test_cache_read(self) -> None:
        """Test reading from cache."""
        cached_csv = """datetime,value,station_id
2020-01-01 00:00:00,30.5,FRE
2020-01-01 01:00:00,31.2,FRE"""

        # Create the actual dataframe that would be returned from cache
        cached_df = pd.read_csv(io.StringIO(cached_csv))
        cached_df["datetime"] = pd.to_datetime(cached_df["datetime"])

        with patch("inundation.fremont.cache_exists", return_value=True):
            with patch("inundation.fremont.pd.read_csv") as mock_read:
                mock_read.return_value = cached_df
                result = get_fre(use_cache=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "datetime" in result.columns

    def test_download_error_handling(self) -> None:
        """Test error handling for download failures."""
        with patch("inundation.fremont.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Connection failed")

            with patch("inundation.fremont.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download data"):
                    get_fre(use_cache=False)

    def test_default_end_date_is_today(self) -> None:
        """Test that default end date is set to today."""
        mock_csv = """Station ID,Sensor Number,Dur Code,Date Time,Data Flag,Value
FRE,1,H,2020-01-01 00:00,0,30.5"""

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with patch("inundation.fremont.pd.DataFrame.to_csv"):
                    get_fre(use_cache=False)

            # Verify the URL was called with today's date
            called_url = mock_get.call_args[0][0]
            from datetime import datetime

            today = datetime.now().strftime("%Y-%m-%d")
            assert f"End={today}" in called_url

    def test_end_date_none_converts_to_today(self) -> None:
        """Test that end=None is converted to today's date."""
        mock_csv = """Station ID,Sensor Number,Dur Code,Date Time,Data Flag,Value
FRE,1,H,2020-01-01 00:00,0,30.5"""

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = mock_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with patch("inundation.fremont.pd.DataFrame.to_csv"):
                    get_fre(end=None, use_cache=False)

            # Verify the URL was called with today's date
            called_url = mock_get.call_args[0][0]
            from datetime import datetime

            today = datetime.now().strftime("%Y-%m-%d")
            assert f"End={today}" in called_url
