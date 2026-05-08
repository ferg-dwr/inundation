# Dayflow (CNRA) Test Fixtures

This directory contains synthetic JSON metadata and CSV fixtures that mimic responses from the [California Natural Resources Agency (CNRA)](https://data.cnra.ca.gov/dataset/dayflow) for the Dayflow dataset.

## Used By

`tests/test_api_edge_cases.py` - Edge case and error handling tests for `get_dayflow()`

## API Workflow

The Dayflow API requires **two requests**:

1. **Metadata request** - Returns JSON with URLs to multiple CSV files
2. **CSV downloads** - One or more CSV files containing actual flow data

Our fixtures mimic both stages of this workflow.

## File Reference

### Metadata Files (JSON)

#### `valid_metadata.json`
**Purpose:** Normal CNRA dataset metadata

**Contents:**
- DCAT-formatted JSON metadata
- Two CSV download URLs (different time periods)
- One PDF entry (to test filtering for CSV-only)
- Realistic structure matching real CNRA responses

**Used in tests:**
- `TestDayflowMetadataParsing::test_valid_metadata_extracts_csv_urls`
- `TestDayflowPartialFailures` (multiple tests)

**Sample structure:**
```json
{
  "@graph": [
    {
      "@type": "dcat:Distribution",
      "dct:format": "CSV",
      "dcat:accessURL": {
        "@id": "https://data.cnra.ca.gov/.../dayflow-2010-2024.csv"
      }
    }
  ]
}
```

---

#### `empty_metadata.json`
**Purpose:** Valid JSON metadata but no downloadable CSVs

**Contents:**
- Valid JSON structure
- No CSV distribution entries
- Only the dataset description

**Used in tests:**
- `TestDayflowMetadataParsing::test_empty_metadata_raises_error`

**Why it matters:** If CNRA temporarily removes all CSV files (e.g., during maintenance), our code should fail with a clear error message, not silently return empty data.

---

#### `malformed_metadata.json`
**Purpose:** Invalid JSON syntax

**Contents:**
- Broken JSON (intentionally not valid)
- Cannot be parsed by `json.loads()`

**Used in tests:**
- `TestDayflowMetadataParsing::test_malformed_metadata_raises_error`

**Why it matters:** If CNRA's API returns an HTML error page or other non-JSON content, the package should fail gracefully with a clear error.

---

### CSV Response Files

#### `valid_response.csv`
**Purpose:** Normal Dayflow CSV response

**Contents:**
- 5 days of dayflow data (2020-01-01 to 2020-01-05)
- All required columns: Year, Mo, Day, Date, SAC, YOLO, etc.
- Realistic flow values (SAC: 15000-16000, YOLO: 1000-4500)
- Day 5 has YOLO=4500 cfs to test the Yolo flow correction trigger

**Used in tests:**
- `TestDayflowMetadataParsing::test_valid_metadata_extracts_csv_urls`
- `TestDayflowPartialFailures` (multiple tests)

**Sample structure:**
```csv
Year,Mo,Day,Date,SAC,YOLO,CSMR,MOKE,MISC,Other,EAST,TOT,EXPORTS
2020,1,1,1/1/2020,15234,1234,567,89,45,123,17292,17292,3000
```

---

#### `missing_columns.csv`
**Purpose:** Response missing the required SAC and YOLO columns

**Contents:**
- Only Year, Mo, Day, Date columns
- Missing flow data columns

**Used in tests:**
- `TestDayflowMissingFields::test_missing_columns_handled`

**Why it matters:** API format changes could result in renamed or missing columns. Tests verify graceful handling.

## CNRA Dayflow API Reference

The fixtures mimic responses from this endpoint:

**Metadata:**
```
https://data.cnra.ca.gov/dataset/06ee2016-b138-47d7-9e85-f46fae674536.jsonld
```

**CSV files:** Listed in metadata response

For details, see [CNRA Open Data Portal](https://data.cnra.ca.gov/dataset/dayflow).

## Updating These Fixtures

To capture a fresh metadata response:

```bash
# Capture real CNRA metadata
curl "https://data.cnra.ca.gov/dataset/06ee2016-b138-47d7-9e85-f46fae674536.jsonld" \
  > tests/fixtures/dayflow/valid_metadata.json
```

To capture a CSV file (URL will be in the metadata):

```bash
# Get URL from metadata, then:
curl "<csv-url-from-metadata>" \
  > tests/fixtures/dayflow/valid_response.csv
```

Then verify tests still pass:
```bash
pytest tests/test_api_edge_cases.py -v
```

## Notable Test Data

### High Yolo Flow Day

`valid_response.csv` includes Jan 5, 2020 with `YOLO=4500` cfs. This is the threshold for "Jessica's correction" in the inundation calculation:

> If yolo_dayflow ≥ 4000 cfs AND previous inund_days > 0, then continue counting inundation days.

This makes the fixture useful for testing the full integration with `calc_inundation()` if needed.

## Why Synthetic Fixtures?

These fixtures are hand-crafted (not captured from live APIs) because:

1. **Reproducibility** - Same data every time, no surprises
2. **Speed** - No network calls during tests
3. **Reliability** - Tests don't fail due to API outages
4. **Coverage** - Can construct edge cases that rarely occur in real data
5. **Maintenance** - Don't need to refresh when APIs change format

For verification against the real API, see `tests/test_integration.py` (runs in `live-integration-tests.yml` workflow).
