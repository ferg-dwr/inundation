# inundation

[![CI](https://github.com/ferg-dwr/inundation/workflows/CI/badge.svg)](https://github.com/ferg-dwr/inundation/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

A Python package for calculating Yolo Bypass inundation duration from water flow and stage height data.

> **Note:** This is a Python translation of the original [R package](https://github.com/goertler/inundation) by Clark & Goertler (2022). Please cite both the R package release and the original research when using this tool. See [NOTICE.md](NOTICE.md) for full attribution.

## Overview

`inundation` downloads and processes water flow and stage height data to calculate the number of inundation days and whether inundation is occurring in the Yolo Bypass—a critical ecological habitat in California's Sacramento Valley.

The package integrates two complementary datasets:

- **CDEC Data** — Fremont Weir stage height measurements from the [California Department of Water Resources](https://cdec.water.ca.gov/)
- **Dayflow Data** — Modeled daily flow data from the [California Natural Resources Agency](https://data.cnra.ca.gov/dataset/dayflow)

## Installation

### From PyPI (when available)

```bash
pip install inundation
```

### From GitHub (development)

```bash
pip install git+https://github.com/ferg-dwr/inundation.git
```

### With development dependencies

```bash
git clone https://github.com/ferg-dwr/inundation.git
cd inundation
pip install -e ".[dev]"
```

## Quick Start

### Calculate inundation duration

```python
from inundation import calc_inundation

# Download all data and calculate inundation days
inun = calc_inundation()

# View the results
print(inun.head())
print(inun.info())
```

### Access individual datasets

```python
from inundation import get_fre, get_dayflow

# Get Fremont Weir stage height (Sacramento River)
fre = get_fre()

# Get dayflow data (Sacramento River and Yolo Bypass)
dayflow = get_dayflow()
```

### Manage cache

The package caches downloaded data locally for fast repeated access. Three flags control caching behavior:

```python
from inundation import get_fre, get_dayflow

# Default - reads from cache if available, writes after download
fre = get_fre()

# Force fresh data, but still update cache for next call
fre = get_fre(refresh=True)

# Don't touch the cache at all (no read, no write)
fre = get_fre(use_cache=False)
```

**Cache management functions:**

```python
from inundation.cache import show_cache, clear_cache

# View cached files with rich metadata
entries = show_cache()
for entry in entries:
    print(f"{entry['filename']}: {entry['row_count']} rows, downloaded {entry['downloaded_at']}")

# Clear all caches
clear_cache()

# Clear only Fremont Weir caches
clear_cache(dataset="fre")

# Clear caches older than 7 days
clear_cache(older_than_days=7)
```

**📖 For detailed information about caching behavior, design philosophy, and best practices, see [docs/caching.md](docs/caching.md).**

## Data Sources

- **Fremont Weir (FRE):** Hourly stage height measurements of the Sacramento River starting January 1, 1984
- **Dayflow:** Daily modeled flow data for Sacramento River and Yolo Bypass starting October 1, 1955

The inundation duration calculation begins February 1, 1984 due to an ongoing flood event when the FRE dataset became available (mid-November 1983).

⚠️ **Data Quality Note:** Years 1989–1991 contain four days with potentially suspect FRE values. See the documentation for quality control details.

## Output

The `calc_inundation()` function returns a pandas DataFrame with:

| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | Date of observation |
| `sac` | float | Sacramento River flow (dayflow) |
| `yolo_dayflow` | float | Yolo Bypass flow (dayflow) |
| `height_sac` | float | Sacramento River stage height (feet, Fremont Weir) |
| `inund_days` | int | Cumulative inundation days since event started |
| `inundation` | int | Binary indicator: 1 = inundation occurring, 0 = no inundation |

## Inundation Definition

An inundation event is defined as:

- **Before October 3, 2016:** Sacramento River stage height ≥ 33.5 feet
- **After October 3, 2016:** Sacramento River stage height ≥ 32.0 feet

These thresholds correspond to when water spills over the Fremont Weir into the Yolo Bypass.

## Citation

If you use this software, please cite it using the metadata from the [`CITATION.cff`](CITATION.cff) file. See [NOTICE.md](NOTICE.md) for full attribution.

### Cite the Python Package

```bibtex
@software{romero_galvan_2026,
  title = {inundation: Python Package for Yolo Bypass Inundation Duration},
  author = {Romero Galvan, Fernando E. and Clark, Jeanette and Goertler, Pascale A.L.},
  year = {2026},
  url = {https://github.com/ferg-dwr/inundation},
  version = {0.1.0}
}
```

### Cite the Original R Package

```bibtex
@software{clark_goertler_2022,
  title = {inundation},
  author = {Clark, Jeanette and Goertler, Pascale A.L.},
  year = {2022},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.6450272},
  url = {https://zenodo.org/records/6450272}
}
```

### Cite the Original Research

If you use the inundation calculation methodology, please cite the original research:

Goertler, P. A. L., Sommer, T., Satterthwaite, W. H., & Schreier, B. M. (2017). Ecological patterns of species dominance in Yolo Bypass, California. *Ecology of Freshwater Fish*, 26(3), 415–426. https://doi.org/10.1111/eff.12372

## References

- Original R package (Zenodo): https://zenodo.org/records/6450272
- Original R package (GitHub): https://github.com/goertler/inundation
- California Department of Water Resources (CDEC): https://cdec.water.ca.gov/
- California Natural Resources Agency (Dayflow): https://data.cnra.ca.gov/dataset/dayflow

## Development

### Setting up development environment

```bash
git clone https://github.com/ferg-dwr/inundation.git
cd inundation
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"
```

### Set up pre-commit hooks (recommended)

Pre-commit hooks automatically run linting and formatting before each commit, catching issues early:

```bash
pip install pre-commit
pre-commit install
```

Once installed, hooks run automatically on every `git commit`. To run them manually:

```bash
pre-commit run --all-files
```

### Running tests

```bash
pytest                    # Run all tests
pytest --cov             # Run with coverage report
pytest -m "not integration"  # Skip integration tests (faster)
```

### Code quality

CI verifies that committed code passes all checks. **Run these locally before committing:**

```bash
ruff check .              # Lint code (auto-fixes with --fix)
ruff check . --fix        # Lint and auto-fix issues
black .                   # Format code
mypy src/inundation       # Type check
pytest                    # Run tests
```

> **Note:** CI will reject PRs that fail these checks. Pre-commit hooks (above) automatically run most of these for you.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest`, `ruff check`, `mypy`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## License

This project is licensed under the Apache License, Version 2.0—see the [LICENSE.md](LICENSE.md) file for details. See [NOTICE.md](NOTICE.md) for attribution and acknowledgments.

The original R package is also licensed under Apache License 2.0 and was created by Jeanette Clark and Pascale A.L. Goertler.

## Acknowledgments

- **Original R package:** Jeanette Clark and Pascale A.L. Goertler ([Zenodo](https://zenodo.org/records/6450272))
- **Python translation:** Fernando E. Romero Galvan (California Department of Water Resources)
- **AI assistance:** This Python translation was developed with assistance from AI code generation (Anthropic Claude). See [NOTICE.md](NOTICE.md) for details.
- **Data sources:**
  - California Department of Water Resources (CDEC Fremont Weir)
  - California Natural Resources Agency (Dayflow)
- **Scientific foundation:** [Goertler et al. (2017)](https://onlinelibrary.wiley.com/doi/10.1111/eff.12372)

## Questions or Issues?

Please open an issue on [GitHub](https://github.com/ferg-dwr/inundation/issues) or refer to the [original R package documentation](https://github.com/goertler/inundation).
