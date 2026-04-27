# inundation

[![Tests](https://github.com/ferg-dwr/inundation/workflows/CI/badge.svg)](https://github.com/ferg-dwr/inundation/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/ferg-dwr/inundation)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for calculating and analyzing Yolo Bypass inundation duration based on Sacramento River stage height and Dayflow data.

## Overview

The Yolo Bypass is an important flood management and ecological feature in California's Sacramento-San Joaquin Delta. This package downloads and processes data from two sources to calculate when the Bypass is inundated:

- **Fremont Weir Stage Height** (CDEC): Sacramento River water level measurements (hourly)
- **Dayflow Data** (CNRA): Modeled daily flows of Sacramento River and Yolo Bypass

Inundation occurs when the Sacramento River stage height exceeds critical thresholds:
- **Before Oct 3, 2016**: ≥ 33.5 feet
- **After Oct 3, 2016**: ≥ 32.0 feet (datum shift)

The package includes special corrections based on hydrological research to refine inundation estimates.

## Features

- ✅ **Automated Data Downloads**: Fetch latest Fremont Weir and Dayflow data from official sources
- ✅ **Smart Caching**: Store downloaded data locally for fast subsequent calls
- ✅ **Quality Control**: Filter unrealistic values; impute missing data using exponential smoothing
- ✅ **Datum Adjustment**: Handle October 3, 2016 datum shift automatically
- ✅ **Special Corrections**: Apply Jessica's Yolo flow correction and 1995/2019 special cases
- ✅ **Full Test Coverage**: 51 unit tests + 9 integration tests (95% coverage)
- ✅ **Production Ready**: Type hints, error handling, comprehensive documentation
- ✅ **Pandas 2.x Compatible**: Modern pandas API with no deprecated functions

## Installation

### Via pip (from GitHub)

```bash
pip install git+https://github.com/ferg-dwr/inundation.git
```

### From source

```bash
git clone https://github.com/ferg-dwr/inundation.git
cd inundation
pip install -e .
```

### Development installation (with test dependencies)

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from inundation import get_fre, get_dayflow, calc_inundation

# Get individual datasets
fre = get_fre()  # Fremont Weir stage height
dayflow = get_dayflow()  # Sacramento River and Yolo Bypass flows

# Calculate inundation
inun = calc_inundation()

print(inun.head())
#                    date      sac  yolo_dayflow  height_sac  inund_days  inundation
# 0 1984-02-01  6897.833333       854.166667   33.486000           1           1
# 1 1984-02-02  6627.500000       854.166667   33.600000           2           1
# 2 1984-02-03  5987.500000       704.166667   33.700000           3           1
# ...
```

### Analyze Results

```python
# Summary statistics
total_inundation_days = inun['inundation'].sum()
pct_inundated = 100 * inun['inundation'].mean()

print(f"Total inundation days: {total_inundation_days}")
print(f"Percentage inundated: {pct_inundated:.2f}%")

# Year-by-year analysis
yearly = inun.groupby(inun['date'].dt.year).agg({
    'inundation': 'sum',           # days inundated that year
    'height_sac': ['mean', 'max']  # stage height statistics
})
```

### Save Results

```python
# Export to CSV
inun.to_csv('inundation_results.csv', index=False)

# Filter and save recent data
recent = inun[inun['date'] >= '2020-01-01']
recent.to_csv('inundation_2020_present.csv', index=False)
```

### Cache Management

```python
from inundation import show_cache, clear_cache

# View cached files
print(show_cache())

# Force fresh download (skip cache)
fre = get_fre(use_cache=False)

# Clear all cached data
clear_cache()
```

## Output Data

### DataFrame Columns

The `calc_inundation()` function returns a DataFrame with these columns:

| Column         | Type       | Description                                     |
|----------------|------------|-------------------------------------------------|
| `date`         | datetime64 | Date of measurement                             |
| `sac`          | float      | Sacramento River flow (dayflow, cfs)            |
| `yolo_dayflow` | float      | Yolo Bypass flow (dayflow, cfs)                 |
| `height_sac`   | float      | Sacramento River stage height (feet)            |
| `inund_days`   | int        | Cumulative inundation days since event started  |
| `inundation`   | int        | Binary indicator (1=inundated, 0=not inundated) |

### Interpretation

- **`inund_days`**: Counter that increments each day when water level is above threshold, resets to 0 when water recedes
- **`inundation`**: 1 when `inund_days > 0`, 0 otherwise
- Data spans from February 1, 1984 to present

## Data Sources

### Fremont Weir Stage Height
- **Source**: California Data Exchange Center (CDEC)
- **Frequency**: Hourly measurements
- **Station**: FRE (Fremont Weir)
- **URL**: https://cdec.water.ca.gov/

### Dayflow Data
- **Source**: California Natural Resources Agency (CNRA)
- **Frequency**: Daily averages
- **Coverage**: October 1, 1955 to present
- **URL**: https://data.cnra.ca.gov/dataset/dayflow

## Examples

### Example 1: Run complete workflow

```bash
python examples/basic_usage.py
```

This script demonstrates all main features with detailed output.

### Example 2: Jupyter Notebook

See `examples/inundation_analysis.ipynb` for an interactive walkthrough with visualizations.

### Example 3: Production Script

```python
#!/usr/bin/env python3
"""Production script for inundation analysis."""

from inundation import calc_inundation
import pandas as pd

# Calculate inundation
inun = calc_inundation()

# Generate summary report
summary = {
    'total_records': len(inun),
    'date_range': f"{inun['date'].min().date()} to {inun['date'].max().date()}",
    'total_inundation_days': int(inun['inundation'].sum()),
    'pct_inundated': round(100 * inun['inundation'].mean(), 2),
    'max_stage_height': round(inun['height_sac'].max(), 2),
}

# Save results
inun.to_csv('inundation_current.csv', index=False)

# Print report
print("\n=== INUNDATION ANALYSIS REPORT ===")
for key, value in summary.items():
    print(f"{key}: {value}")
```

## Testing

### Run all tests

```bash
pytest tests/ -v
```

### Run with coverage report

```bash
pytest tests/ --cov=src/inundation --cov-report=html
```

### Run integration tests only

```bash
pytest tests/test_integration.py -v -m integration
```

### Run quick unit tests

```bash
pytest tests/ -k "not integration"
```

## Code Quality

All code is validated with:

- **mypy**: Type checking (`mypy src/`)
- **ruff**: Linting and formatting (`ruff check .`)
- **black**: Code formatting (`black src/ tests/`)
- **pytest**: Testing with coverage (`pytest tests/ --cov`)

## Project Structure

```
inundation/
├── src/inundation/
│   ├── __init__.py                # Main package exports
│   ├── cache.py                   # Cache management (show_cache, clear_cache)
│   ├── fremont.py                 # get_fre() - download Fremont Weir data
│   ├── dayflow.py                 # get_dayflow() - download Dayflow data
│   └── inundation.py              # calc_inundation() - main calculation
├── tests/
│   ├── test_cache.py              # Unit tests for cache functions
│   ├── test_fremont.py            # Unit tests for get_fre()
│   ├── test_dayflow.py            # Unit tests for get_dayflow()
│   ├── test_inundation.py         # Unit tests for calc_inundation()
│   └── test_integration.py        # Integration tests with real data
├── examples/
│   ├── basic_usage.py             # Complete usage example script
│   └── inundation_analysis.ipynb  # Interactive Jupyter notebook
├── pyproject.toml                 # Project configuration
├── README.md                      # This file
└── LICENSE                        # MIT License
```

## Performance

- **First run**: ~10-30 seconds (downloads data from CDEC and CNRA)
- **Cached runs**: <1 second (reads from local cache)
- **Cached location**: `~/.cache/inundation/` (Linux/Mac) or `%APPDATA%\inundation\` (Windows)

Cache is automatically used if available; use `use_cache=False` to force fresh downloads.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes and add tests
4. Ensure all tests pass (`pytest tests/`)
5. Submit a pull request

## Citation

If you use this package in research, please cite the original R package and this Python translation:

**Original R Package:**
> Goertler, C.M., Sommer, T., Monsen, N., Sutton, R., & Kirsch, J. (2017).
> Ecological patterns of species dominance in Yolo Bypass, California.
> Ecology of Freshwater Fish, 26(3), 415-426.
> https://doi.org/10.1111/eff.12372

**Python Translation:**
> Galvan, F. (2024). inundation: Python package for Yolo Bypass inundation analysis.
> https://github.com/ferg-dwr/inundation

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: https://github.com/ferg-dwr/inundation/issues
- **Documentation**: https://github.com/ferg-dwr/inundation#readme
- **Data Sources**:
  - CDEC: https://cdec.water.ca.gov/
  - CNRA Dayflow: https://data.cnra.ca.gov/dataset/dayflow

## Acknowledgments

- Original R package authors: Christopher M. Goertler and collaborators
- Data providers: California Department of Water Resources (CDEC), California Natural Resources Agency (CNRA)
- Python translation: Fermin Galvan (DWR)