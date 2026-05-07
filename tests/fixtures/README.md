# Test Fixtures

This directory contains test fixtures for **scientific correctness tests** in `test_scientific_correctness.py`.

## Purpose

These fixtures provide **known inputs with known expected outputs** to verify that the inundation calculation logic produces correct results. Unlike structural tests that just verify "the function returns a DataFrame," these tests verify **exact expected values** for specific scenarios.

## Test Scenarios

### Scenario 1: `simple_above_threshold/`
**Input:** 3 consecutive days at 35 ft (well above 33.5 ft threshold)  
**Period:** 2020-01-01 to 2020-01-03  
**Expected:**
- All 3 days: `inundation = 1`
- `inund_days = [1, 2, 3]`

**Why:** Tests basic threshold logic and counter increment.

---

### Scenario 2: `simple_below_threshold/`
**Input:** 3 consecutive days at 30 ft (well below 33.5 ft threshold)  
**Period:** 2020-01-01 to 2020-01-03  
**Expected:**
- All 3 days: `inundation = 0`
- All 3 days: `inund_days = 0`

**Why:** Tests that low water doesn't trigger inundation.

---

### Scenario 3: `crossing_threshold_pre_2016/`
**Input:** 5 days going from below to above threshold (33.5 ft)  
**Period:** 2016-01-01 to 2016-01-05  
**Heights:** 33.0, 33.4, 33.5, 34.0, 34.5  
**Expected:**
- Day 1: `inundation = 0` (below 33.5)
- Day 2: `inundation = 0` (still below)
- Day 3: `inundation = 1` (at threshold, `inund_days = 1`)
- Day 4: `inundation = 1` (`inund_days = 2`)
- Day 5: `inundation = 1` (`inund_days = 3`)

**Why:** Tests pre-2016 threshold of exactly 33.5 ft.

---

### Scenario 4: `crossing_threshold_post_2016/`
**Input:** 5 days going from below to above threshold (32.0 ft)  
**Period:** 2017-01-01 to 2017-01-05  
**Heights:** 31.5, 31.9, 32.0, 32.5, 33.0  
**Expected:**
- Day 1: `inundation = 0` (below 32.0)
- Day 2: `inundation = 0` (still below)
- Day 3: `inundation = 1` (at threshold, `inund_days = 1`)
- Day 4: `inundation = 1` (`inund_days = 2`)
- Day 5: `inundation = 1` (`inund_days = 3`)

**Why:** Tests post-2016 threshold change to 32.0 ft (datum shift).

---

### Scenario 5: `datum_change_2016/`
**Input:** Days spanning the October 3, 2016 datum change  
**Period:** 2016-09-30 to 2016-10-05  
**Heights:** All at 32.5 ft  
**Expected:**
- Pre-Oct 3, 2016: `inundation = 0` (32.5 < 33.5)
- Post-Oct 3, 2016: `inundation = 1` (32.5 ≥ 32.0)

**Why:** Tests that the datum change is applied correctly.

---

### Scenario 6: `yolo_flow_correction/`
**Input:** Inundation event followed by stage drop, but high Yolo flow  
**Period:** 2020-01-01 to 2020-01-04  
**Heights:** 34.0, 34.0, 30.0, 30.0  
**Yolo flows:** 1000, 1000, 4500, 4500  
**Expected:**
- Day 1: `inund_days = 1`
- Day 2: `inund_days = 2`
- Day 3: `inund_days = 3` (extended by Jessica's correction: yolo ≥ 4000 + prev > 0)
- Day 4: `inund_days = 4` (continues due to high flow)

**Why:** Tests Jessica's Yolo flow correction (yolo_dayflow ≥ 4000 cfs extends inundation).

---

### Scenario 7: `inundation_reset/`
**Input:** Inundation event followed by drop in both stage and flow  
**Period:** 2020-01-01 to 2020-01-04  
**Heights:** 34.0, 34.0, 30.0, 30.0  
**Yolo flows:** 1000, 1000, 1000, 1000 (low)  
**Expected:**
- Day 1: `inund_days = 1`
- Day 2: `inund_days = 2`
- Day 3: `inund_days = 0` (reset - no Yolo correction)
- Day 4: `inund_days = 0`

**Why:** Tests that inundation properly resets when conditions return to normal.

---

### Scenario 8: `binary_indicator_consistency/`
**Input:** Mixed inundation and non-inundation days  
**Period:** 2020-01-01 to 2020-01-05  
**Heights:** 34.0, 30.0, 34.0, 30.0, 34.0  
**Expected:**
- `inundation` matches `(inund_days > 0).astype(int)` for all rows

**Why:** Tests that the binary indicator is always consistent with the counter.

---

## Generation Method

These fixtures are **manually-defined** based on the documented inundation rules:

- **Pre-2016-10-03 threshold:** ≥ 33.5 ft
- **Post-2016-10-03 threshold:** ≥ 32.0 ft
- **Yolo correction:** yolo_dayflow ≥ 4000 cfs + previous inund_days > 0 → extend counter
- **Counter behavior:** Increments daily during inundation, resets to 0 when conditions clear

## Why Not Use the R Package as Reference?

Ideally, expected outputs would be generated from the original R package. However:

1. The R package's tests only verify column existence (not specific values)
2. Our scenarios are simple enough that expected values can be computed from documented rules
3. These tests guarantee deterministic behavior of our Python implementation

If you have access to the R package, you can verify these scenarios by running:

```r
library(inundation)
# Mock the data sources with our test inputs
result <- calc_inundation()
```

## Tolerance

For floating-point comparisons (e.g., `height_sac` after exponential weighted mean):
- **Stage height:** ±0.1 ft tolerance
- **Inundation counter (`inund_days`):** Exact match (integer)
- **Binary indicator (`inundation`):** Exact match (0 or 1)

## File Format

Each scenario directory contains:
- `fre_input.csv` - Mock Fremont Weir hourly data
- `dayflow_input.csv` - Mock Dayflow daily data
- `expected_output.csv` - Expected `calc_inundation()` output