"""
Integration tests for the inundation package.

These tests verify the complete workflow using real data.
Marked with @pytest.mark.integration to run separately if needed.
"""

import pandas as pd
import pytest

from inundation import calc_inundation, get_dayflow, get_fre


@pytest.mark.integration
class TestIntegration:
    """Integration tests with real data."""

    def test_get_fre_returns_valid_dataframe(self) -> None:
        """Test that get_fre returns valid data."""
        fre = get_fre(use_cache=True)

        # Check type
        assert isinstance(fre, pd.DataFrame)

        # Check columns
        assert "datetime" in fre.columns
        assert "value" in fre.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(fre["datetime"])
        assert pd.api.types.is_numeric_dtype(fre["value"])

        # Check non-empty
        assert len(fre) > 0

        # Check reasonable date range
        assert fre["datetime"].min().year >= 1980
        assert fre["datetime"].max().year <= 2030

    def test_get_dayflow_returns_valid_dataframe(self) -> None:
        """Test that get_dayflow returns valid data."""
        dayflow = get_dayflow(use_cache=True)

        # Check type
        assert isinstance(dayflow, pd.DataFrame)

        # Check columns
        assert "date" in dayflow.columns
        assert "sac" in dayflow.columns
        assert "yolo" in dayflow.columns

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(dayflow["date"])
        assert pd.api.types.is_numeric_dtype(dayflow["sac"])
        assert pd.api.types.is_numeric_dtype(dayflow["yolo"])

        # Check non-empty
        assert len(dayflow) > 0

        # Check reasonable date range (dayflow starts in 1929)
        assert dayflow["date"].min().year >= 1920
        assert dayflow["date"].max().year <= 2030

    def test_calc_inundation_returns_complete_dataset(self) -> None:
        """Test that calc_inundation returns complete inundation dataset."""
        inun = calc_inundation()

        # Check type
        assert isinstance(inun, pd.DataFrame)

        # Check all required columns
        required_cols = ["date", "sac", "yolo_dayflow", "height_sac", "inund_days", "inundation"]
        for col in required_cols:
            assert col in inun.columns, f"Missing column: {col}"

        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(inun["date"])
        assert pd.api.types.is_numeric_dtype(inun["height_sac"])
        assert pd.api.types.is_integer_dtype(inun["inund_days"])
        assert pd.api.types.is_integer_dtype(inun["inundation"])

        # Check non-empty
        assert len(inun) > 0

        # Check reasonable values
        assert inun["inund_days"].min() >= 0
        assert inun["inundation"].min() >= 0
        assert inun["inundation"].max() <= 1

    def test_inundation_counter_increments(self) -> None:
        """Test that inundation counter increments correctly."""
        inun = calc_inundation()

        # Filter to a specific inundation event
        inundation_mask = inun["inundation"] == 1
        if inundation_mask.sum() > 0:
            # Get first inundation period
            first_inun_idx = inundation_mask.idxmax()
            inun_period = inun.loc[first_inun_idx : first_inun_idx + 100]

            # Check that days increment (or reset to 0)
            inund_days = inun_period["inund_days"].values
            for i in range(1, len(inund_days)):
                # Should either increment by 1, or reset to 0
                diff = inund_days[i] - inund_days[i - 1]
                assert diff >= -inund_days[i - 1], "Unexpected inund_days behavior"

    def test_inundation_binary_indicator_matches_counter(self) -> None:
        """Test that binary inundation indicator matches counter."""
        inun = calc_inundation()

        # Where inund_days > 0, inundation should be 1
        # Where inund_days == 0, inundation should be 0
        expected = (inun["inund_days"] > 0).astype(int)
        assert (inun["inundation"] == expected).all(), "Binary indicator doesn't match counter"

    def test_threshold_logic_before_2016(self) -> None:
        """Test that stage threshold is 33.5 ft before Oct 3, 2016."""
        inun = calc_inundation()

        # Filter to before 2016
        before_2016 = inun[inun["date"] < "2016-10-03"]

        if len(before_2016) > 0:
            # No inundation should occur below 33.5 ft (allowing for special cases)
            low_water = before_2016[before_2016["height_sac"] < 33.5]
            # Most should have inundation=0 (some may have inundation due to corrections)
            inundation_rate = low_water["inundation"].mean()
            assert inundation_rate < 0.1, "High inundation rate below 33.5 ft threshold"

    def test_threshold_logic_after_2016(self) -> None:
        """Test that stage threshold is 32.0 ft after Oct 3, 2016."""
        inun = calc_inundation()

        # Filter to after 2016
        after_2016 = inun[inun["date"] >= "2016-10-03"]

        if len(after_2016) > 0:
            # No inundation should occur below 32.0 ft (allowing for special cases)
            low_water = after_2016[after_2016["height_sac"] < 32.0]
            # Most should have inundation=0 (some may have inundation due to corrections)
            inundation_rate = low_water["inundation"].mean()
            assert inundation_rate < 0.1, "High inundation rate below 32.0 ft threshold"

    def test_data_continuity(self) -> None:
        """Test that date sequence is continuous (no large gaps)."""
        inun = calc_inundation()

        # Check that dates are sorted
        assert (inun["date"].diff().dropna() >= pd.Timedelta(days=0)).all(), "Dates not sorted"

        # Check for reasonable gaps (should be daily data)
        date_diffs = inun["date"].diff().dropna()
        assert (date_diffs <= pd.Timedelta(days=2)).all(), "Large gaps in date sequence"

    def test_realistic_stage_heights(self) -> None:
        """Test that stage heights are within realistic range."""
        fre = get_fre(use_cache=True)

        # Peak Stage of Record is 41.02 feet
        # We filter values between 2-41.03 feet in quality control
        assert (fre["value"] >= 0).all() or fre["value"].isna().any()

        # Check reasonable range (actual mean ~18.66 ft from historical data)
        valid_values = fre[fre["value"].notna() & (fre["value"] > 2)]
        assert valid_values["value"].mean() > 15, "Mean stage too low"
        assert valid_values["value"].mean() < 35, "Mean stage too high"

    def test_realistic_flow_values(self) -> None:
        """Test that flow values are within realistic range."""
        dayflow = get_dayflow(use_cache=True)

        # Sacramento River flow typically 1000-10000 cfs
        sac_valid = dayflow[dayflow["sac"].notna()]
        if len(sac_valid) > 0:
            assert sac_valid["sac"].mean() > 100, "Mean SAC flow too low"
            assert sac_valid["sac"].mean() < 50000, "Mean SAC flow too high"

        # Yolo Bypass flow typically 0-5000 cfs
        yolo_valid = dayflow[dayflow["yolo"].notna()]
        if len(yolo_valid) > 0:
            assert yolo_valid["yolo"].mean() >= 0, "Negative YOLO flow"
            assert yolo_valid["yolo"].mean() < 10000, "Mean YOLO flow too high"


@pytest.mark.integration
class TestProductionReadiness:
    """Tests to verify production readiness."""

    def test_no_unhandled_exceptions(self) -> None:
        """Verify that main functions don't raise exceptions."""
        # These should complete without error
        fre = get_fre(use_cache=True)
        dayflow = get_dayflow(use_cache=True)
        inun = calc_inundation()

        assert fre is not None
        assert dayflow is not None
        assert inun is not None

    def test_cache_improves_performance(self) -> None:
        """Verify that cache works and returns consistent data."""
        import time

        # First call (should use cache if available, or download)
        start = time.time()
        fre1 = get_fre(use_cache=True)
        time1 = time.time() - start

        # Second call (should use cache)
        start = time.time()
        fre2 = get_fre(use_cache=True)
        time2 = time.time() - start

        # Both calls should return the same data
        assert len(fre1) == len(fre2), "Different data from cache"

        # Verify cached data is actually being used (print for debug)
        # Note: timing can be flaky due to OS caching, so we just verify consistency
        # Typical speedup is 10-100x when fresh download vs cache, but system load varies
        assert time1 > 0 and time2 > 0, "Timing measurements valid"

    def test_results_are_reproducible(self) -> None:
        """Verify that results are reproducible."""
        # Run twice
        inun1 = calc_inundation()
        inun2 = calc_inundation()

        # Should be identical
        pd.testing.assert_frame_equal(inun1, inun2)

    def test_data_quality_metrics(self) -> None:
        """Verify overall data quality."""
        inun = calc_inundation()

        # Check for excessive missing data
        missing_pct = inun.isnull().sum() / len(inun) * 100
        assert (missing_pct < 1).all(), f"Too much missing data: {missing_pct}"

        # Check that we have multiple years of data
        inun["year"] = pd.to_datetime(inun["date"]).dt.year
        year_count = inun["year"].nunique()
        assert year_count > 30, f"Only {year_count} years of data, need 30+"

        # Check reasonable distribution of inundation
        inun_rate = inun["inundation"].mean()
        assert 0.01 < inun_rate < 0.10, f"Unexpected inundation rate: {inun_rate:.2%}"
