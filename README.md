# inundation

[![CI](https://github.com/ferg-dwr/inundation/workflows/CI/badge.svg)](https://github.com/ferg-dwr/inundation/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for calculating Yolo Bypass inundation duration from water flow and stage height data.

> **Note:** This is a Python translation of the original [R package](https://github.com/goertler/inundation) by Clark & Goertler (2022). Please cite both the R package release and the original research when using this tool.

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

```python
from inundation.cache import show_cache, clear_cache

# View cached files
files = show_cache()
print(f"Cached files: {files}")

# Clear cache if needed
clear_cache()
```

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

If you use this software, please cite it using the metadata from the `CITATION.cff` file.

### Cite the Python Package

```bibtex
@software{romero_galvan_2026,
  title = {inundation: Python Package for Yolo Bypass Inundation Duration},
  author = {Romero Galvan, Fernando E. and Goertler, Pascale A.L.},
  year = {2026},
  url = {https://github.com/ferg-dwr/inundation},
  version = {0.1.0}
}
```

### Cite the Original R Package

```bibtex
@software{goertler_2022,
  title = {inundation: Calculate number of inundation days},
  author = {Goertler, Pascale A.L.},
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

### Running tests

```bash
pytest                    # Run all tests
pytest --cov             # Run with coverage report
pytest -m "not slow"     # Skip slow tests
```

### Code quality

```bash
ruff check .             # Lint code
black .                  # Format code
mypy src/inundation      # Type check
```

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

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.

The original R package is also MIT licensed and was created by Christopher M. Goertler and collaborators at UC Davis.

## Acknowledgments

- **Original R package:** Pascale A.L. Goertler (UC Davis)
- **Python translation:** Fernando E. Romero Galvan (California Department of Water Resources)
- **Data sources:** 
  - California Department of Water Resources (CDEC Fremont Weir)
  - California Natural Resources Agency (Dayflow)
- **Scientific foundation:** [Goertler et al. (2017)](https://onlinelibrary.wiley.com/doi/10.1111/eff.12372)

## Questions or Issues?

Please open an issue on [GitHub](https://github.com/ferg-dwr/inundation/issues) or refer to the [original R package documentation](https://github.com/goertler/inundation).
