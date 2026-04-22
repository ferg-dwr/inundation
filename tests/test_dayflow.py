"""Tests for the dayflow module."""

import io
import json
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from inundation.dayflow import get_dayflow


class TestGetDayflow:
    """Test the get_dayflow function."""

    def test_cache_read(self) -> None:
        """Test reading from cache."""
        cached_csv = """date,sac,yolo
1955-10-01,1234.5,567.8
1955-10-02,1250.3,580.1"""

        cached_df = pd.read_csv(io.StringIO(cached_csv))
        cached_df["date"] = pd.to_datetime(cached_df["date"])

        with patch("inundation.dayflow.cache_exists", return_value=True):
            with patch("inundation.dayflow.pd.read_csv") as mock_read:
                mock_read.return_value = cached_df
                result = get_dayflow(use_cache=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "date" in result.columns
        assert "sac" in result.columns
        assert "yolo" in result.columns

    def test_download_with_metadata(self) -> None:
        """Test downloading dayflow data with JSON metadata parsing."""
        # Mock metadata response
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file1.csv"},
                },
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file2.csv"},
                },
                {"dct:format": "PDF", "dcat:accessURL": {"@id": "somepdf.pdf"}},
            ]
        }

        csv_data = """Date,SAC,YOLO
1955-10-01,1234.5,567.8
1955-10-02,1250.3,580.1"""

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                # Setup mock responses
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                csv_response = Mock()
                csv_response.text = csv_data
                csv_response.raise_for_status = Mock()

                # First call returns metadata, subsequent calls return CSV
                mock_get.side_effect = [metadata_response, csv_response, csv_response]

                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    result = get_dayflow(use_cache=False)

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 2
        assert "date" in result.columns
        assert "sac" in result.columns
        assert "yolo" in result.columns

    def test_missing_yolo_column(self) -> None:
        """Test handling of missing YOLO column in data."""
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file1.csv"},
                }
            ]
        }

        # CSV without YOLO column
        csv_data = """Date,SAC
1955-10-01,1234.5
1955-10-02,1250.3"""

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                csv_response = Mock()
                csv_response.text = csv_data
                csv_response.raise_for_status = Mock()

                mock_get.side_effect = [metadata_response, csv_response]

                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    result = get_dayflow(use_cache=False)

        # Should have YOLO column (possibly with NaN values)
        assert "yolo" in result.columns

    def test_download_error_handling(self) -> None:
        """Test error handling for download failures."""
        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                mock_get.side_effect = requests.ConnectionError("Network error")

                with pytest.raises(RuntimeError, match="Failed to download"):
                    get_dayflow(use_cache=False)

    def test_json_parse_error(self) -> None:
        """Test error handling for invalid JSON metadata."""
        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
                metadata_response.raise_for_status = Mock()

                mock_get.return_value = metadata_response

                with pytest.raises(RuntimeError, match="Failed to parse"):
                    get_dayflow(use_cache=False)

    def test_no_csv_urls_in_metadata(self) -> None:
        """Test error when no CSV URLs found in metadata."""
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "PDF",
                    "dcat:accessURL": {"@id": "somefile.pdf"},
                }
            ]
        }

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                mock_get.return_value = metadata_response

                with pytest.raises(RuntimeError, match="No CSV download URLs"):
                    get_dayflow(use_cache=False)

    def test_no_downloadable_data(self) -> None:
        """Test error when all CSV downloads fail."""
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file1.csv"},
                }
            ]
        }

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                csv_response = Mock()
                csv_response.raise_for_status.side_effect = requests.RequestException("Failed")

                mock_get.side_effect = [metadata_response, csv_response]

                with pytest.raises(RuntimeError, match="Failed to download any"):
                    get_dayflow(use_cache=False)

    def test_duplicate_removal(self) -> None:
        """Test that duplicates are removed."""
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file1.csv"},
                },
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file2.csv"},
                },
            ]
        }

        csv_data = """Date,SAC,YOLO
1955-10-01,1234.5,567.8
1955-10-01,1234.5,567.8"""

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                csv_response = Mock()
                csv_response.text = csv_data
                csv_response.raise_for_status = Mock()

                mock_get.side_effect = [
                    metadata_response,
                    csv_response,
                    csv_response,
                ]

                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    result = get_dayflow(use_cache=False)

        # Should have 2 rows from file1 + 2 from file2, but duplicates removed
        assert len(result) <= 2

    def test_date_sorting(self) -> None:
        """Test that results are sorted by date."""
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file1.csv"},
                }
            ]
        }

        csv_data = """Date,SAC,YOLO
1955-10-03,1200.0,545.3
1955-10-01,1234.5,567.8
1955-10-02,1250.3,580.1"""

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                csv_response = Mock()
                csv_response.text = csv_data
                csv_response.raise_for_status = Mock()

                mock_get.side_effect = [metadata_response, csv_response]

                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    result = get_dayflow(use_cache=False)

        # Check that dates are in ascending order
        dates = result["date"].values
        assert all(dates[i] <= dates[i + 1] for i in range(len(dates) - 1))

    def test_type_conversion(self) -> None:
        """Test that columns are properly converted to correct types."""
        mock_metadata = {
            "@graph": [
                {
                    "dct:format": "CSV",
                    "dcat:accessURL": {"@id": "https://data.cnra.ca.gov/dataset/results/file1.csv"},
                }
            ]
        }

        csv_data = """Date,SAC,YOLO
1955-10-01,1234.5,567.8
1955-10-01,invalid,580.1"""

        with patch("inundation.dayflow.cache_exists", return_value=False):
            with patch("inundation.dayflow.requests.get") as mock_get:
                metadata_response = Mock()
                metadata_response.json.return_value = mock_metadata
                metadata_response.raise_for_status = Mock()

                csv_response = Mock()
                csv_response.text = csv_data
                csv_response.raise_for_status = Mock()

                mock_get.side_effect = [metadata_response, csv_response]

                with patch("inundation.dayflow.pd.DataFrame.to_csv"):
                    result = get_dayflow(use_cache=False)

        # Check types
        assert pd.api.types.is_datetime64_any_dtype(result["date"])
        assert result["sac"].dtype in ["float64", "Float64"]
        assert result["yolo"].dtype in ["float64", "Float64"]
        # Invalid numeric should become NaN
        assert pd.isna(result.loc[1, "sac"])
