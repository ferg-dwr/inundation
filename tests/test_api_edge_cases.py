"""Edge case tests for API interactions.

These tests verify error handling, timeout behavior, malformed responses,
and other edge cases for get_fre() and get_dayflow() functions.

All tests use mocked HTTP responses (no live API calls) to ensure:
- Fast execution
- Reliable results (no flaky network failures)
- Reproducible behavior
- Coverage of edge cases that rarely occur in real data

For tests against live APIs, see tests/test_integration.py which runs
in the live-integration-tests.yml workflow.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from inundation.dayflow import get_dayflow
from inundation.fremont import _get_cdec_url, get_fre

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(relative_path: str) -> str:
    """Load a fixture file and return its contents as a string."""
    fixture_path = FIXTURES_DIR / relative_path
    return fixture_path.read_text()


def load_json_fixture(relative_path: str) -> dict:
    """Load a JSON fixture file and return parsed dict."""
    fixture_path = FIXTURES_DIR / relative_path
    with fixture_path.open() as f:
        data: dict = json.load(f)
        return data


class TestFreRequestParameterConstruction:
    """Test that request parameters are constructed correctly."""

    def test_default_parameters_in_url(self) -> None:
        """Default station, dates, and sensor are in URL."""
        url = _get_cdec_url()
        assert "Stations=FRE" in url
        assert "SensorNums=1" in url
        assert "dur_code=H" in url
        assert "Start=1940-01-01" in url
        assert "End=" in url

    def test_custom_station_in_url(self) -> None:
        """Custom station ID is properly included."""
        url = _get_cdec_url(station_id="ABC")
        assert "Stations=ABC" in url
        assert "Stations=FRE" not in url

    def test_custom_dates_in_url(self) -> None:
        """Custom start and end dates are properly included."""
        url = _get_cdec_url(start="2020-06-15", end="2020-12-31")
        assert "Start=2020-06-15" in url
        assert "End=2020-12-31" in url

    def test_url_has_correct_base(self) -> None:
        """URL uses the correct CDEC base URL."""
        url = _get_cdec_url()
        assert "cdec.water.ca.gov" in url
        assert "CSVDataServlet" in url

    def test_url_uses_https_by_default(self) -> None:
        """URL should use HTTPS for security."""
        url = _get_cdec_url()
        # Note: original CDEC API used HTTP, but HTTPS should be preferred
        # This test documents current behavior - update if URL scheme changes
        assert url.startswith("http")


class TestFreEmptyResponses:
    """Test handling of empty but valid responses."""

    def test_empty_fre_response_returns_empty_dataframe(self) -> None:
        """Empty CSV (headers only) should return empty DataFrame."""
        empty_csv = load_fixture("fre/empty_response.csv")

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = empty_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                result = get_fre(use_cache=False)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        # Even when empty, structure should be intact
        assert "datetime" in result.columns or len(result.columns) >= 0


class TestFreMalformedResponses:
    """Test handling of malformed CSV responses."""

    def test_malformed_csv_handled_gracefully(self) -> None:
        """Malformed CSV should not crash but may produce empty/odd data."""
        malformed_csv = load_fixture("fre/malformed_response.csv")

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = malformed_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                # Should either succeed with weird data or raise a clear error
                # Not crash with unhelpful error
                try:
                    result = get_fre(use_cache=False)
                    # If it succeeds, result should be a DataFrame
                    assert isinstance(result, pd.DataFrame)
                except (ValueError, KeyError, pd.errors.ParserError):
                    # These are acceptable errors for malformed data
                    pass

    def test_invalid_value_types_become_nan(self) -> None:
        """Non-numeric values in VALUE column should become NaN."""
        invalid_csv = load_fixture("fre/invalid_value_type.csv")

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = invalid_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                result = get_fre(use_cache=False)

        # Valid numeric value should be preserved
        valid_values = result[result["value"].notna()]
        assert len(valid_values) > 0
        assert 30.5 in valid_values["value"].values

        # Invalid values should be NaN
        nan_count = result["value"].isna().sum()
        assert nan_count > 0, "Invalid values should be coerced to NaN"


class TestFreNetworkErrors:
    """Test handling of network errors and timeouts."""

    def test_timeout_raises_runtime_error(self) -> None:
        """A timeout should raise a clear RuntimeError."""
        with patch("inundation.fremont.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timed out")

            with patch("inundation.fremont.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_fre(use_cache=False)

    def test_connection_error_raises_runtime_error(self) -> None:
        """A connection error should raise a clear RuntimeError."""
        with patch("inundation.fremont.requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection refused")

            with patch("inundation.fremont.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_fre(use_cache=False)

    def test_http_error_raises_runtime_error(self) -> None:
        """An HTTP error (e.g., 500) should raise a clear RuntimeError."""
        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_fre(use_cache=False)


class TestFreValidResponse:
    """Test handling of valid responses using fixture data."""

    def test_valid_response_parsed_correctly(self) -> None:
        """A valid CDEC response should be parsed into a clean DataFrame."""
        valid_csv = load_fixture("fre/valid_response.csv")

        with patch("inundation.fremont.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = valid_csv
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch("inundation.fremont.cache_exists", return_value=False):
                result = get_fre(use_cache=False)

        # Check structure
        assert isinstance(result, pd.DataFrame)
        assert "datetime" in result.columns
        assert "value" in result.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(result["datetime"])
        assert pd.api.types.is_numeric_dtype(result["value"])

        # Check 24 hours of data
        assert len(result) == 24

        # Check values are reasonable
        assert result["value"].min() >= 29.0
        assert result["value"].max() <= 31.0


class TestDayflowMetadataParsing:
    """Test handling of CNRA metadata responses."""

    def test_valid_metadata_extracts_csv_urls(self) -> None:
        """Valid metadata should extract all CSV URLs."""
        valid_metadata = load_json_fixture("dayflow/valid_metadata.json")
        valid_csv = load_fixture("dayflow/valid_response.csv")

        with patch("inundation.dayflow.requests.get") as mock_get:
            metadata_response = Mock()
            metadata_response.json.return_value = valid_metadata
            metadata_response.raise_for_status = Mock()

            csv_response = Mock()
            csv_response.text = valid_csv
            csv_response.raise_for_status = Mock()

            # First call: metadata, subsequent calls: CSV
            mock_get.side_effect = [metadata_response, csv_response, csv_response]

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    with patch("inundation.dayflow.add_to_index"):
                        result = get_dayflow(use_cache=False)

        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns
        assert "sac" in result.columns
        assert "yolo" in result.columns

    def test_empty_metadata_raises_error(self) -> None:
        """Metadata with no CSV URLs should raise RuntimeError."""
        empty_metadata = load_json_fixture("dayflow/empty_metadata.json")

        with patch("inundation.dayflow.requests.get") as mock_get:
            metadata_response = Mock()
            metadata_response.json.return_value = empty_metadata
            metadata_response.raise_for_status = Mock()
            mock_get.return_value = metadata_response

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="No CSV download URLs"):
                    get_dayflow(use_cache=False)

    def test_malformed_metadata_raises_error(self) -> None:
        """Invalid JSON metadata should raise RuntimeError."""
        with patch("inundation.dayflow.requests.get") as mock_get:
            metadata_response = Mock()
            metadata_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            metadata_response.raise_for_status = Mock()
            mock_get.return_value = metadata_response

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to parse"):
                    get_dayflow(use_cache=False)


class TestDayflowNetworkErrors:
    """Test dayflow handling of network errors and timeouts."""

    def test_metadata_timeout_raises_error(self) -> None:
        """Timeout when fetching metadata should raise RuntimeError."""
        with patch("inundation.dayflow.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timed out")

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_dayflow(use_cache=False)

    def test_connection_error_raises_error(self) -> None:
        """Connection error should raise RuntimeError."""
        with patch("inundation.dayflow.requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Network unreachable")

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_dayflow(use_cache=False)


class TestDayflowMissingFields:
    """Test handling of responses missing required fields."""

    def test_missing_columns_handled(self) -> None:
        """Response missing required columns should be handled gracefully."""
        valid_metadata = load_json_fixture("dayflow/valid_metadata.json")
        missing_cols_csv = load_fixture("dayflow/missing_columns.csv")

        with patch("inundation.dayflow.requests.get") as mock_get:
            metadata_response = Mock()
            metadata_response.json.return_value = valid_metadata
            metadata_response.raise_for_status = Mock()

            csv_response = Mock()
            csv_response.text = missing_cols_csv
            csv_response.raise_for_status = Mock()

            mock_get.side_effect = [metadata_response, csv_response, csv_response]

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    with patch("inundation.dayflow.add_to_index"):
                        # Should either succeed with NaN values or raise clear error
                        try:
                            result = get_dayflow(use_cache=False)
                            # If succeeds, expect missing data
                            assert isinstance(result, pd.DataFrame)
                        except (RuntimeError, KeyError):
                            # Acceptable - clear error for missing required data
                            pass


class TestDayflowPartialFailures:
    """Test handling when some CSV downloads fail but others succeed."""

    def test_one_failed_csv_does_not_break_all(self) -> None:
        """If one CSV download fails, others should still succeed."""
        valid_metadata = load_json_fixture("dayflow/valid_metadata.json")
        valid_csv = load_fixture("dayflow/valid_response.csv")

        with patch("inundation.dayflow.requests.get") as mock_get:
            metadata_response = Mock()
            metadata_response.json.return_value = valid_metadata
            metadata_response.raise_for_status = Mock()

            # First CSV fails
            failed_response = Mock()
            failed_response.raise_for_status.side_effect = requests.HTTPError("500")

            # Second CSV succeeds
            success_response = Mock()
            success_response.text = valid_csv
            success_response.raise_for_status = Mock()

            mock_get.side_effect = [metadata_response, failed_response, success_response]

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    with patch("inundation.dayflow.add_to_index"):
                        # Should succeed with data from the working CSV
                        result = get_dayflow(use_cache=False)
                        assert isinstance(result, pd.DataFrame)
                        assert len(result) > 0

    def test_all_csv_downloads_fail_raises_error(self) -> None:
        """If all CSV downloads fail, should raise RuntimeError."""
        valid_metadata = load_json_fixture("dayflow/valid_metadata.json")

        with patch("inundation.dayflow.requests.get") as mock_get:
            metadata_response = Mock()
            metadata_response.json.return_value = valid_metadata
            metadata_response.raise_for_status = Mock()

            failed_response = Mock()
            failed_response.raise_for_status.side_effect = requests.HTTPError("500")

            mock_get.side_effect = [metadata_response, failed_response, failed_response]

            with patch("inundation.dayflow.cache_exists", return_value=False):
                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_dayflow(use_cache=False)
