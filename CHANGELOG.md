# Changelog

All notable changes to the `inundation` package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Request-aware caching system (#6)
  - Cache files now include request parameters in filename (e.g., `fre_FRE_2020-01-01_2020-12-31.csv`)
  - Single `cache_index.json` tracks metadata for all cached files
  - Metadata includes: source URL, request parameters, download timestamp, package version, row count, file size
- New `refresh` parameter for `get_fre()` and `get_dayflow()` (#6)
- Enhanced `show_cache()` returns metadata-rich entries (#6)
- Targeted cache clearing in `clear_cache()` (#6)
- New `docs/caching.md` with comprehensive caching guide (#6)
- Scientific correctness tests with expected values (#5)
  - 18 deterministic tests verifying inundation calculation logic
  - Tests for threshold behavior, counter logic, Yolo correction, missing data
  - Documentation in `tests/fixtures/README.md`
- `.pre-commit-config.yaml` for local development checks (#4)
- `NOTICE.md` with full attribution per Apache 2.0 requirements (#2)
- `.gitattributes` for consistent line endings across platforms
- Comprehensive API edge case tests in `tests/test_api_edge_cases.py` (#7)
  - 17+ tests covering empty responses, malformed CSVs, missing columns
  - Tests for network errors (timeout, connection, HTTP errors)
  - Tests for request parameter construction
  - Tests for partial failures in dayflow downloads
- Synthetic test fixtures in `tests/fixtures/` (#7)
  - FRE fixtures: valid, empty, malformed, missing column, invalid types
  - Dayflow fixtures: valid metadata/response, empty, malformed, missing columns
  - Comprehensive READMEs documenting each fixture and its purpose
- New live integration tests workflow `.github/workflows/live-integration-tests.yml` (#7)
  - Runs weekly via cron schedule (Mondays 6 AM UTC)
  - Manual trigger via workflow_dispatch
  - Notifies on failure with troubleshooting steps

### Changed
- `use_cache=False` now disables BOTH reading AND writing to cache (#6)
- License changed from MIT to Apache 2.0 (#2)
- CI workflow no longer auto-fixes code (#4)
- Releases now triggered by version tags only (#4)
- Updated GitHub Actions to latest versions (#4)
- Updated authors and attribution (#2)
- Integration tests now properly separated from PR CI (#7)
  - PR CI runs only fast mocked tests
  - Live API tests run on schedule and on demand
  - Faster, more reliable CI feedback for contributors

### Fixed
- Pandas 2.x compatibility issues
- mypy type errors in caching module (#6)
- Removed non-PEP 621 fields from `pyproject.toml` (#11)
- Applied ruff and black formatting consistently (#13, #14)
- Normalized line endings to LF across all text files
- CI now properly excludes integration tests with `-m "not integration"`

## [0.1.0] - 2026-05-08

### Added
- Initial Python translation of the R `inundation` package
- `get_fre()` - Download Fremont Weir stage height data from CDEC
- `get_dayflow()` - Download California Dayflow data from CNRA
- `calc_inundation()` - Calculate Yolo Bypass inundation duration
- `show_cache()` and `clear_cache()` - Cache management utilities
- Comprehensive test suite
- Type hints throughout
- Full documentation and examples
- Support for Python 3.10+

[Unreleased]: https://github.com/ferg-dwr/inundation/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ferg-dwr/inundation/releases/tag/v0.1.0