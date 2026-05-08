"""Cache management for the inundation package.

This module provides request-aware caching with the following design philosophy:

CACHING BEHAVIOR
================

The cache is designed to be **predictable and safe** for scientific workflows.
Three flags control caching:

1. `use_cache=True` (default): Read from cache if matching entry exists,
   write to cache after successful download.

2. `use_cache=False`: Disables BOTH reading AND writing to cache.
   - Use this when you want a one-off query that doesn't affect cache state
   - Useful for testing, exploring, or when you want full reproducibility

3. `refresh=True`: Force a fresh download, but still write to cache.
   - Use this when you want fresh data but want caching enabled for next call
   - Useful for daily reports or when you suspect cache is stale

CACHE FILE STRUCTURE
====================

Cache files use human-readable names that include request parameters:
- `fre_FRE_2020-01-01_2020-12-31.csv`
- `dayflow.csv` (no request parameters needed)

A single `cache_index.json` file in the cache directory tracks all cached
data with metadata:
- Source URL
- Request parameters
- Download date/time
- Package version
- Row count
- File size

This makes the cache:
- Self-describing (you can see what's cached without parsing data)
- Request-aware (different requests = different cache files)
- Safe (matching cache only returned for matching requests)
- Auditable (when was data downloaded? from where?)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import appdirs

# Index file tracks all cached data and metadata
INDEX_FILENAME = "cache_index.json"


def get_cache_dir() -> Path:
    """Return the cache directory path, creating it if needed.

    Returns
    -------
    Path
        Path to the cache directory.
    """
    cache_dir = Path(appdirs.user_cache_dir("inundation"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_file(filename: str) -> Path:
    """Return the full path to a cache file.

    Parameters
    ----------
    filename : str
        Name of the cache file.

    Returns
    -------
    Path
        Full path to the cache file.
    """
    return get_cache_dir() / filename


def get_index_path() -> Path:
    """Return the path to the cache index file.

    Returns
    -------
    Path
        Path to cache_index.json
    """
    return get_cache_dir() / INDEX_FILENAME


def load_index() -> dict[str, Any]:
    """Load the cache index, creating an empty one if it doesn't exist.

    Returns
    -------
    dict
        Cache index as a dictionary mapping filenames to metadata.
    """
    index_path = get_index_path()
    if not index_path.exists():
        return {}

    try:
        with index_path.open("r") as f:
            data: dict[str, Any] = json.load(f)
            return data
    except (json.JSONDecodeError, OSError):
        # If index is corrupted, start fresh
        return {}


def save_index(index: dict[str, Any]) -> None:
    """Save the cache index to disk.

    Parameters
    ----------
    index : dict
        Cache index to save.
    """
    index_path = get_index_path()
    with index_path.open("w") as f:
        json.dump(index, f, indent=2, default=str)


def make_cache_key(prefix: str, params: dict[str, Any]) -> str:
    """Create a human-readable cache filename from request parameters.

    Parameters
    ----------
    prefix : str
        Dataset name (e.g., "fre", "dayflow")
    params : dict
        Request parameters that affect the result.

    Returns
    -------
    str
        Human-readable cache filename.

    Examples
    --------
    >>> make_cache_key("fre", {"station_id": "FRE", "start": "2020-01-01", "end": "2020-12-31"})
    'fre_FRE_2020-01-01_2020-12-31.csv'
    """
    if not params:
        return f"{prefix}.csv"

    # Build human-readable filename from key parameters
    parts = [prefix]
    for key in sorted(params.keys()):
        value = params[key]
        if value is not None:
            # Sanitize value for filename (no spaces, slashes, etc.)
            safe_value = str(value).replace("/", "-").replace(" ", "_")
            parts.append(safe_value)

    return "_".join(parts) + ".csv"


def add_to_index(
    filename: str,
    params: dict[str, Any],
    source_url: str,
    row_count: int,
    package_version: str = "0.1.0",
) -> None:
    """Add or update a cache entry in the index.

    Parameters
    ----------
    filename : str
        Cache filename
    params : dict
        Request parameters used to generate this cache
    source_url : str
        URL the data was downloaded from
    row_count : int
        Number of rows in the cached data
    package_version : str
        Version of the inundation package that created the cache
    """
    index = load_index()

    file_path = get_cache_file(filename)
    file_size = file_path.stat().st_size if file_path.exists() else 0

    index[filename] = {
        "params": params,
        "source_url": source_url,
        "downloaded_at": datetime.now().isoformat(),
        "package_version": package_version,
        "row_count": row_count,
        "file_size_bytes": file_size,
    }

    save_index(index)


def get_cache_metadata(filename: str) -> dict[str, Any] | None:
    """Get metadata for a cached file.

    Parameters
    ----------
    filename : str
        Cache filename to look up

    Returns
    -------
    dict or None
        Metadata dictionary if cache entry exists, None otherwise.
    """
    index = load_index()
    return index.get(filename)


def cache_exists(filename: str) -> bool:
    """Check if a cache file exists.

    Parameters
    ----------
    filename : str
        Name of the cache file.

    Returns
    -------
    bool
        True if cache file exists, False otherwise.
    """
    return get_cache_file(filename).exists()


def show_cache() -> list[dict[str, Any]]:
    """Show summary of all cached files with their metadata.

    Returns
    -------
    list[dict]
        List of dictionaries with cache file information including:
        - filename
        - source_url
        - downloaded_at
        - row_count
        - file_size_bytes
        - params

    Examples
    --------
    >>> entries = show_cache()
    >>> for entry in entries:
    ...     print(f"{entry['filename']}: {entry['row_count']} rows")
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return []

    index = load_index()
    entries = []

    # Get all CSV files in cache (skip index file)
    csv_files = sorted(cache_dir.glob("*.csv"))

    for file_path in csv_files:
        filename = file_path.name
        metadata = index.get(filename, {})

        entry = {
            "filename": filename,
            "source_url": metadata.get("source_url", "unknown"),
            "downloaded_at": metadata.get("downloaded_at", "unknown"),
            "row_count": metadata.get("row_count", 0),
            "file_size_bytes": metadata.get("file_size_bytes", file_path.stat().st_size),
            "params": metadata.get("params", {}),
            "package_version": metadata.get("package_version", "unknown"),
        }
        entries.append(entry)

    return entries


def clear_cache(
    dataset: str | None = None,
    older_than_days: int | None = None,
) -> int:
    """Clear cached files with optional filters.

    Parameters
    ----------
    dataset : str, optional
        Only clear caches starting with this prefix (e.g., "fre", "dayflow").
        If None, clears all caches.
    older_than_days : int, optional
        Only clear caches older than this many days. If None, clears regardless of age.

    Returns
    -------
    int
        Number of files removed.

    Examples
    --------
    Clear all caches:

    >>> clear_cache()
    3

    Clear only Fremont Weir caches:

    >>> clear_cache(dataset="fre")
    1

    Clear caches older than 7 days:

    >>> clear_cache(older_than_days=7)
    2

    Clear Fremont caches older than 30 days:

    >>> clear_cache(dataset="fre", older_than_days=30)
    1
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return 0

    index = load_index()
    files_removed = 0
    now = datetime.now()

    # Get list of cache files (excluding index file)
    csv_files = list(cache_dir.glob("*.csv"))

    for file_path in csv_files:
        filename = file_path.name

        # Filter by dataset name
        if dataset is not None and not filename.startswith(dataset):
            continue

        # Filter by age
        if older_than_days is not None:
            metadata = index.get(filename, {})
            downloaded_str = metadata.get("downloaded_at")

            if downloaded_str:
                try:
                    downloaded_at = datetime.fromisoformat(downloaded_str)
                    age_days = (now - downloaded_at).days
                    if age_days < older_than_days:
                        continue
                except (ValueError, TypeError):
                    # If date parsing fails, skip this file
                    continue
            else:
                # No metadata = use file modification time
                file_age_seconds = now.timestamp() - file_path.stat().st_mtime
                file_age_days = file_age_seconds / 86400
                if file_age_days < older_than_days:
                    continue

        # Remove the file
        file_path.unlink()
        files_removed += 1

        # Remove from index
        if filename in index:
            del index[filename]

    # Save updated index
    save_index(index)

    return files_removed


def matches_cache_request(filename: str, params: dict[str, Any]) -> bool:
    """Check if a cached file matches the given request parameters.

    Parameters
    ----------
    filename : str
        Cache filename to check
    params : dict
        Request parameters to match

    Returns
    -------
    bool
        True if cache matches request parameters, False otherwise.
    """
    metadata = get_cache_metadata(filename)
    if metadata is None:
        return False

    cached_params = metadata.get("params", {})
    return bool(cached_params == params)
