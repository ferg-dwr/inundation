# Changelog

All notable changes to the `inundation` package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Scientific correctness tests with expected values (#5)
  - 18 deterministic tests verifying inundation calculation logic
  - Tests for threshold behavior (pre/post 2016 datum change)
  - Tests for counter increment/reset logic
  - Tests for Yolo flow correction at 4000 cfs
  - Tests for missing-data and imputation behavior
  - Documentation in `tests/fixtures/README.md`
- `CHANGELOG.md` to track package changes
- `NOTICE.md` with full attribution per Apache 2.0 requirements

### Changed
- License changed from MIT to Apache 2.0 (#2)
  - Matches original R package license
  - Copyright assigned to State of California, Department of Water Resources
- Updated CI workflow to remove auto-fixing in `ruff check`
- Releases now triggered by version tags (e.g., `v0.1.0`) instead of every push to main
- Updated GitHub Actions to latest versions:
  - `actions/checkout@v4`
  - `actions/setup-python@v5`
  - `actions/cache@v4`
  - `codecov/codecov-action@v4`
- Updated authors and attribution:
  - Original R package authors: Jeanette Clark and Pascale A.L. Goertler
  - Python translation: Fernando E. Romero Galvan (DWR)
  - Removed incorrect "Christopher M. Goertler" references

### Fixed
- Pandas 2.x compatibility issues (deprecated `fillna(method=...)`)
- Test reliability improvements

## [0.1.0] - Unreleased

### Added
- Initial Python translation of the R `inundation` package
- `get_fre()` - Download Fremont Weir stage height data from CDEC
- `get_dayflow()` - Download California Dayflow data from CNRA
- `calc_inundation()` - Calculate Yolo Bypass inundation duration
- `show_cache()` and `clear_cache()` - Cache management utilities
- Comprehensive test suite (51+ tests)
- Mocked tests for external data downloads
- Integration tests with real data
- Type hints throughout
- Full documentation and examples
- Support for Python 3.10+

[Unreleased]: https://github.com/ferg-dwr/inundation/compare/main...HEAD
[0.1.0]: https://github.com/ferg-dwr/inundation/releases/tag/v0.1.0