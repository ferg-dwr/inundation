# FRE (Fremont Weir / CDEC) Test Fixtures

This directory contains synthetic CSV fixtures that mimic responses from the [CDEC API](https://cdec.water.ca.gov/) for the Fremont Weir (FRE) station.

## Used By

`tests/test_api_edge_cases.py` - Edge case and error handling tests for `get_fre()`

## File Reference

### Valid Responses

#### `valid_response.csv`
**Purpose:** Normal CDEC FRE response

**Contents:**
- 24 hours of stage height data (2020-01-01)
- Hourly readings (DURATION=H)
- Realistic stage height values (29-31 ft)
- All standard columns present

**Used in tests:**
- `TestFreValidResponse::test_valid_response_parsed_correctly`
- Various other tests as a baseline for normal flow

**Sample structure:**
```csv
STATION_ID,DURATION,SENSOR_NUMBER,SENSOR_TYPE,DATE TIME,OBS DATE,VALUE,DATA_FLAG,UNITS
FRE,H,1,STAGE,20200101 0000,20200101 0000,30.5,,FEET
FRE,H,1,STAGE,20200101 0100,20200101 0100,30.6,,FEET
...
```

---

### Edge Case Responses

#### `empty_response.csv`
**Purpose:** Valid CSV with only headers, no data rows

**Contents:**
- CSV header line only
- No data rows

**Used in tests:**
- `TestFreEmptyResponses::test_empty_fre_response_returns_empty_dataframe`

**Why it matters:** APIs sometimes return valid CSVs with no data (e.g., when querying for a date range with no observations). The package should handle this without crashing.

---

#### `invalid_value_type.csv`
**Purpose:** Mix of valid numeric and invalid (non-numeric) values

**Contents:**
- 4 rows with values: `not_a_number`, `---`, `30.5`, `N/A`
- One valid value (30.5) preserved for verification

**Used in tests:**
- `TestFreMalformedResponses::test_invalid_value_types_become_nan`

**Why it matters:** CDEC sometimes returns dashes (`---`) or `N/A` for missing measurements. The package should coerce these to NaN, not crash, and preserve valid numeric values.

---

### Error Cases

#### `malformed_response.csv`
**Purpose:** Completely invalid CSV format

**Contents:**
- Plain text, not actual CSV
- No proper structure

**Used in tests:**
- `TestFreMalformedResponses::test_malformed_csv_handled_gracefully`

**Why it matters:** If CDEC returns an HTML error page or other non-CSV content, the package should fail gracefully with a clear error rather than crashing in an unhelpful way.

---

#### `missing_value_column.csv`
**Purpose:** Response missing the required VALUE column

**Contents:**
- All other columns present
- VALUE column omitted

**Used in tests:**
- (Currently a placeholder - implementation depends on how `get_fre` handles this)

**Why it matters:** API format changes could break our code. This fixture helps test resilience to API schema changes.

## CDEC API Reference

The fixtures mimic responses from this endpoint:
```
https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet
```

Query parameters used:
- `Stations=FRE` - Fremont Weir station
- `SensorNums=1` - Sensor 1 (Stage)
- `dur_code=H` - Hourly data
- `Start=YYYY-MM-DD` - Start date
- `End=YYYY-MM-DD` - End date

For details, see [CDEC's API documentation](https://cdec.water.ca.gov/dynamicapp/wsSensorData).

## Updating These Fixtures

To capture a fresh response from the live API:

```bash
# Capture real CDEC response
curl "https://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet?Stations=FRE&SensorNums=1&dur_code=H&Start=2020-01-01&End=2020-01-02" \
  > tests/fixtures/fre/valid_response.csv
```

Then verify tests still pass:
```bash
pytest tests/test_api_edge_cases.py -v
```

## Why Synthetic Fixtures?

These fixtures are hand-crafted (not captured from live APIs) because:

1. **Reproducibility** - Same data every time, no surprises
2. **Speed** - No network calls during tests
3. **Reliability** - Tests don't fail due to API outages
4. **Coverage** - Can construct edge cases that rarely occur in real data
5. **Maintenance** - Don't need to refresh when APIs change format

For verification against the real API, see `tests/test_integration.py` (runs in `live-integration-tests.yml` workflow).
