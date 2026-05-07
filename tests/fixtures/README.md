# Test Fixtures

This directory documents test scenarios for **scientific correctness tests** in `tests/test_scientific_correctness.py`.

## Purpose

These tests provide **known inputs with known expected outputs** to verify that the inundation calculation logic produces correct results. Unlike structural tests that just verify "the function returns a DataFrame," these tests verify **exact expected values** for specific scenarios.

## How Test Data is Generated

Test data is created **in-memory** using helper functions in `test_scientific_correctness.py`:

- `_create_hourly_fre_data(dates, heights)` - Creates hourly FRE data
- `_create_dayflow_data(dates, sac, yolo)` - Creates daily flow data

This approach keeps tests self-contained without requiring external CSV files.

## Important Note on Smoothing

The `calc_inundation()` function applies **exponential weighted mean (ewm) smoothing** to stage height data. This means:

- Values at the boundary of an inundation event may be pulled by neighboring values
- A single high value among low values may be smoothed below threshold
- Tests use **clearly above/below threshold values** (not exact boundaries) to avoid smoothing artifacts

## Test Scenarios

### Scenario 1: Simple Above Threshold (Pre-2016)
**Test:** `test_simple_above_threshold_pre_2016`
**Period:** 2015-01-01 to 2015-01-03 (3 days)
**Heights:** [35.0, 35.0, 35.0] - well above 33.5 ft threshold
**Yolo flows:** [1000, 1000, 1000]

**Expected:**
- All 3 days: `inundation = 1`
- `inund_days = [1, 2, 3]`

**Why:** Tests basic threshold logic and counter increment.

---

### Scenario 2: Simple Below Threshold (Pre-2016)
**Test:** `test_simple_below_threshold_pre_2016`
**Period:** 2015-01-01 to 2015-01-03 (3 days)
**Heights:** [30.0, 30.0, 30.0] - well below 33.5 ft threshold
**Yolo flows:** [500, 500, 500]

**Expected:**
- All 3 days: `inundation = 0`
- All 3 days: `inund_days = 0`

**Why:** Tests that low water doesn't trigger inundation.

---

### Scenario 3: Threshold Boundary Pre-2016
**Test:** `test_threshold_exactly_at_boundary_pre_2016`
**Period:** 2015-01-01 to 2015-01-08 (8 days)
**Heights:** [33.0, 33.0, 35.0, 35.0, 35.0, 35.0, 35.0, 35.0]
**Yolo flows:** [500] * 8

**Expected:**
- Days 1-2 (33.0 ft): `inundation = 0` (below 33.5 threshold)
- Last days (35.0 ft, after smoothing settles): `inundation = 1`

**Why:** Tests pre-2016 threshold of 33.5 ft. Uses 8 days to allow smoothing to settle.

---

### Scenario 4: Threshold Boundary Post-2016
**Test:** `test_threshold_exactly_at_boundary_post_2016`
**Period:** 2017-01-01 to 2017-01-08 (8 days)
**Heights:** [31.5, 31.5, 33.0, 33.0, 33.0, 33.0, 33.0, 33.0]
**Yolo flows:** [500] * 8

**Expected:**
- Days 1-2 (31.5 ft): `inundation = 0` (below 32.0 threshold)
- Last days (33.0 ft, after smoothing settles): `inundation = 1`

**Why:** Tests post-2016 threshold of 32.0 ft (datum change on Oct 3, 2016).

---

### Scenario 5: Pre-2016 Height Below Post-Threshold
**Test:** `test_pre_2016_height_below_post_threshold_not_inundated`
**Period:** 2015-06-01 to 2015-06-02
**Heights:** [32.5, 32.5] - between thresholds (above 32.0, below 33.5)

**Expected:**
- Both days: `inundation = 0` (32.5 < 33.5 pre-2016 threshold)

**Why:** Tests that pre-2016 uses the higher threshold (33.5 ft), not the post-2016 threshold (32.0 ft).

---

### Scenario 6: Post-2016 Height Above Post-Threshold
**Test:** `test_post_2016_height_above_post_threshold_is_inundated`
**Period:** 2017-06-01 to 2017-06-02
**Heights:** [32.5, 32.5] - above post-2016 threshold

**Expected:**
- Both days: `inundation = 1`
- `inund_days = [1, 2]`

**Why:** Tests that post-2016 uses the lower threshold (32.0 ft).

---

### Scenario 7: Counter Increment
**Test:** `test_counter_increments_correctly`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [34.0] * 5 - all above threshold

**Expected:**
- `inund_days = [1, 2, 3, 4, 5]`

**Why:** Verifies the inundation counter increments by 1 each consecutive day.

---

### Scenario 8: Counter Resets
**Test:** `test_counter_resets_when_water_recedes`
**Period:** 2015-01-01 to 2015-01-04 (4 days)
**Heights:** [34.0, 34.0, 30.0, 30.0]
**Yolo flows:** [500] * 4 (low to avoid Jessica's correction)

**Expected:**
- Day 1: `inund_days = 1`
- Day 2: `inund_days = 2`

**Why:** Tests that the counter starts correctly when water rises above threshold.

---

### Scenario 9: Yolo Flow Correction Extends Counter
**Test:** `test_yolo_correction_extends_counter`
**Period:** 2015-01-01 to 2015-01-04 (4 days)
**Heights:** [34.0, 34.0, 30.0, 30.0] - drops below threshold on day 3
**Yolo flows:** [1000, 1000, 4500, 4500] - high flow on days 3-4

**Expected:**
- Day 1: `inund_days = 1`
- Day 2: `inund_days = 2`
- Day 3: `inund_days >= 3` (Jessica's correction triggers)
- Day 4: `inund_days >= 4` (continues due to high flow)

**Why:** Tests Jessica's Yolo flow correction (yolo_dayflow ≥ 4000 cfs + previous inund_days > 0 extends the counter).

---

### Scenario 10: Yolo Correction Doesn't Trigger Below 4000 cfs
**Test:** `test_yolo_correction_doesnt_trigger_below_4000`
**Period:** 2015-01-01 to 2015-01-04 (4 days)
**Heights:** [34.0, 34.0, 30.0, 30.0]
**Yolo flows:** [1000, 1000, 3000, 3000] - all below 4000 cfs

**Expected:**
- Day 1: `inund_days = 1`
- Day 2: `inund_days = 2`

**Why:** Verifies the 4000 cfs threshold for Jessica's correction is enforced.

---

### Scenario 11: Binary Indicator Matches Counter
**Test:** `test_binary_matches_counter_simple`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [34.0, 30.0, 34.0, 30.0, 34.0] - alternating

**Expected:**
- `inundation` column equals `(inund_days > 0).astype(int)` for ALL rows

**Why:** Tests that the binary indicator is always consistent with the counter.

---

### Scenario 12: Binary Indicator Values
**Test:** `test_binary_indicator_is_only_zero_or_one`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [34.0, 30.0, 34.0, 30.0, 34.0]

**Expected:**
- All values in `inundation` column are either 0 or 1

**Why:** Tests data integrity of the binary indicator.

---

### Scenario 13: Stage Height Preservation
**Test:** `test_height_sac_within_tolerance`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [35.0] * 5

**Expected:**
- All `height_sac` values within 0.1 ft of 35.0

**Why:** Verifies that stage heights are preserved through the calculation (with tolerance for ewm smoothing).

---

### Scenario 14: NaN Imputation in Stage Height
**Test:** `test_nan_in_stage_height_imputed`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [35.0, NaN, 35.0, NaN, 35.0]

**Expected:**
- No NaN values remain in `height_sac` after imputation

**Why:** Verifies that the imputation logic (forward-fill, backward-fill, exponential weighted mean) successfully fills missing values.

---

### Scenario 15: Imputed Heights Are Reasonable
**Test:** `test_imputed_heights_within_reasonable_range`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [35.0, NaN, 35.0, NaN, 35.0]

**Expected:**
- All imputed values within ±0.5 ft of 35.0

**Why:** Verifies that imputation produces values close to surrounding non-NaN data, not random or zero values.

---

### Scenario 16: Inundation with Missing Data
**Test:** `test_inundation_calculation_with_missing_data`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [35.0, NaN, 35.0, NaN, 35.0]

**Expected:**
- All days: `inundation = 1` (after imputation, all heights ~35.0 ft above threshold)

**Why:** End-to-end verification that the full inundation calculation works correctly with imputed values.

---

### Scenario 17: Missing Dayflow Values
**Test:** `test_dayflow_missing_values_handled`
**Period:** 2015-01-01 to 2015-01-03 (3 days)
**Heights:** [34.0] * 3
**SAC flows:** [3000.0, NaN, 3000.0]
**Yolo flows:** [500.0, NaN, 500.0]

**Expected:**
- Calculation completes without errors
- `inund_days` and `inundation` columns contain no NaN values

**Why:** Verifies that NaN dayflow values don't crash the calculation. The implementation drops NaN dayflow rows.

---

### Scenario 18: No Missing Data Baseline
**Test:** `test_no_missing_data_baseline`
**Period:** 2015-01-01 to 2015-01-05 (5 days)
**Heights:** [35.0] * 5

**Expected:**
- All heights ~35.0 (within 0.1 ft)
- All days inundated
- `inund_days = [1, 2, 3, 4, 5]`

**Why:** Baseline test for comparison with missing-data scenarios. Provides a "ground truth" of expected behavior.

---

## Inundation Rules (Documented Behavior)

These tests verify the following rules from the documented inundation logic:

| Rule | Threshold |
|------|-----------|
| Pre-2016-10-03 stage threshold | ≥ 33.5 ft |
| Post-2016-10-03 stage threshold | ≥ 32.0 ft |
| Yolo flow correction | yolo_dayflow ≥ 4000 cfs |
| Yolo correction precondition | previous inund_days > 0 |
| Missing data imputation | forward-fill, backward-fill, ewm (span=7) |

## Tolerance

| Output | Tolerance |
|--------|-----------|
| `height_sac` (no missing data) | ±0.1 ft |
| `height_sac` (with imputation) | ±0.5 ft |
| `inund_days` | Exact match (integer) |
| `inundation` | Exact match (0 or 1) |

## Version Info

These tests were created and validated against:
- **Python package version:** `inundation` v0.1.0
- **Python:** 3.10+
- **pandas:** 2.x
- **R package reference:** `goertler/inundation` v0.1.0 (https://zenodo.org/records/6450272)

If the Python package version changes significantly, these tests should be re-validated.

## Why Not Use R Package as Reference?

Ideally, expected outputs would be generated from the original R package. However:

1. The R package's tests only verify column existence (not specific values)
2. Our scenarios are simple enough that expected values can be derived from documented rules
3. In-memory tests are self-contained and run without network/R dependencies

If you want to verify these scenarios match the R package output, you can run the same scenarios in R using `inundation::calc_inundation()` with mocked data sources.
