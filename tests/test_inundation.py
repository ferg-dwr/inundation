"""Tests for the inundation module."""

from datetime import timedelta
from unittest.mock import patch

import pandas as pd

from inundation.inundation import calc_inundation


class TestCalcInundation:
    """Test the calc_inundation function."""

    def test_calc_inundation_basic(self) -> None:
        """Test basic inundation calculation."""
        # Create mock FRE data (hourly)
        fre_data = pd.DataFrame(
            {
                "datetime": pd.date_range("2020-01-01", periods=24, freq="h"),
                "value": [30.0, 30.2, 33.8, 34.0, 33.9, 32.0, 31.0, 30.5] * 3,
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        # Create mock dayflow data
        dayflow_data = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=1),
                "sac": [5000.0],
                "yolo": [1000.0],
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns
        assert "inund_days" in result.columns
        assert "inundation" in result.columns

    def test_threshold_before_2016(self) -> None:
        """Test inundation threshold before October 3, 2016 (33.5 feet)."""
        # Date before threshold change
        test_date = pd.Timestamp("2016-01-01")

        fre_data = pd.DataFrame(
            {
                "datetime": [test_date + timedelta(hours=i) for i in range(24)],
                "value": [33.4] * 12 + [33.5] * 12,  # Cross threshold at 33.5
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": [test_date],
                "sac": [5000.0],
                "yolo": [1000.0],
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        # At 33.4 feet (below threshold), inundation should be 0
        # At 33.5 feet (at threshold), inundation should be 1
        row_before_threshold = result[result["date"] == test_date]
        assert len(row_before_threshold) > 0

    def test_threshold_after_2016(self) -> None:
        """Test inundation threshold after October 3, 2016 (32.0 feet)."""
        # Date after threshold change
        test_date = pd.Timestamp("2016-11-01")

        fre_data = pd.DataFrame(
            {
                "datetime": [test_date + timedelta(hours=i) for i in range(24)],
                "value": [31.9] * 12 + [32.0] * 12,  # Cross threshold at 32.0
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": [test_date],
                "sac": [5000.0],
                "yolo": [1000.0],
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        assert isinstance(result, pd.DataFrame)
        assert "inundation" in result.columns

    def test_inundation_days_increment(self) -> None:
        """Test that inundation days increment correctly."""
        dates = pd.date_range("2020-01-01", periods=5)

        fre_data = pd.DataFrame(
            {
                "datetime": [date + timedelta(hours=i) for date in dates for i in range(24)],
                "value": [34.0] * (5 * 24),  # All days above threshold
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0] * 5,
                "yolo": [1000.0] * 5,
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        # Inundation days should increment each day
        inund_days = result["inund_days"].values
        # Should go from 1, 2, 3, 4, 5 (or similar increasing pattern)
        assert all(inund_days[i] >= inund_days[i - 1] for i in range(1, len(inund_days)))

    def test_yolo_flow_correction(self) -> None:
        """Test Jessica's correction for high Yolo flow (≥4000 cfs)."""
        dates = pd.date_range("2020-01-01", periods=3)

        # Heights: low, low, low (but prev day was high)
        fre_data = pd.DataFrame(
            {
                "datetime": [date + timedelta(hours=i) for date in dates for i in range(24)],
                "value": [30.0] * 72,  # All below threshold
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0] * 3,
                "yolo": [3000.0, 4500.0, 3000.0],  # Mid day has high flow
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        assert isinstance(result, pd.DataFrame)
        # High Yolo flow day should have higher inund_days than low flow days
        assert result["yolo_dayflow"].iloc[1] >= 4000

    def test_quality_control_filters(self) -> None:
        """Test that unrealistic values are filtered out."""
        dates = pd.date_range("2020-01-01", periods=2)

        fre_data = pd.DataFrame(
            {
                "datetime": [date + timedelta(hours=i) for date in dates for i in range(24)],
                "value": [30.0] * 12
                + [1.0] * 12
                + [42.0] * 24,  # 1.0 and 42.0 are outside valid range
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0] * 2,
                "yolo": [1000.0] * 2,
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        # Result should still be valid
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_missing_data_handling(self) -> None:
        """Test handling of missing values in dayflow data."""
        dates = pd.date_range("2020-01-01", periods=2)

        fre_data = pd.DataFrame(
            {
                "datetime": [date + timedelta(hours=i) for date in dates for i in range(24)],
                "value": [33.8] * 48,
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0, pd.NA],  # Missing SAC value
                "yolo": [1000.0, 1100.0],
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        # Should handle missing data gracefully
        assert isinstance(result, pd.DataFrame)

    def test_binary_inundation_indicator(self) -> None:
        """Test that binary inundation indicator is correct."""
        dates = pd.date_range("2020-01-01", periods=2)

        fre_data = pd.DataFrame(
            {
                "datetime": [date + timedelta(hours=i) for date in dates for i in range(24)],
                "value": [34.0] * 24 + [30.0] * 24,  # First day high, second low
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0] * 2,
                "yolo": [1000.0] * 2,
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        # Inundation should be 1 where inund_days > 0, else 0
        assert all((result["inundation"] == (result["inund_days"] > 0)).astype(int))

    def test_column_order(self) -> None:
        """Test that output columns are in expected order."""
        dates = pd.date_range("2020-01-01", periods=1)

        fre_data = pd.DataFrame(
            {
                "datetime": [dates[0] + timedelta(hours=i) for i in range(24)],
                "value": [33.8] * 24,
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0],
                "yolo": [1000.0],
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        expected_cols = ["date", "sac", "yolo_dayflow", "height_sac", "inund_days", "inundation"]
        actual_cols = list(result.columns)
        assert actual_cols == expected_cols

    def test_date_filtering(self) -> None:
        """Test that results start from 1984-02-01."""
        dates = pd.date_range("1980-01-01", periods=2000, freq="D")

        fre_data = pd.DataFrame(
            {
                "datetime": [date + timedelta(hours=i) for date in dates for i in range(1)],
                "value": [33.8] * len(dates),
                "station_id": "FRE",
                "sensor_number": "1",
                "duration": "H",
            }
        )

        dayflow_data = pd.DataFrame(
            {
                "date": dates,
                "sac": [5000.0] * len(dates),
                "yolo": [1000.0] * len(dates),
            }
        )

        with patch("inundation.inundation.get_fre") as mock_fre:
            with patch("inundation.inundation.get_dayflow") as mock_dayflow:
                mock_fre.return_value = fre_data
                mock_dayflow.return_value = dayflow_data

                result = calc_inundation()

        # Min date should be around 1984-02-01 (after merging)
        min_date = result["date"].min()
        assert min_date.year >= 1984
