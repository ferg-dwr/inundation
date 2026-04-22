"""Cache utilities for the inundation package.

This module provides utilities for managing cached data files.
Cached files are stored in the user's system cache directory.
"""

from pathlib import Path

import appdirs


def get_cache_dir() -> Path:
    """Get the cache directory for the inundation package.
s
    Creates the directory if it doesn't exist.

    Returns
    -------
    Path
        Path to the inundation cache directory.
    """
    cache_dir = Path(appdirs.user_cache_dir("inundation"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_file(filename: str) -> Path:
    """Get the full path to a cache file.

    Parameters
    ----------
    filename : str
        Name of the cache file (e.g., "fre.csv").

    Returns
    -------
    Path
        Full path to the cache file.
    """
    return get_cache_dir() / filename


def cache_exists(filename: str) -> bool:
    """Check if a cache file exists.

    Parameters
    ----------
    filename : str
        Name of the cache file (e.g., "fre.csv").

    Returns
    -------
    bool
        True if the cache file exists, False otherwise.
    """
    return get_cache_file(filename).exists()


def show_cache() -> list[str]:
    """Show list of cached inundation files.

    Returns
    -------
    list of str
        List of full paths to cached files.

    Examples
    --------
    >>> files = show_cache()
    >>> print(files)
    ['/home/user/.cache/inundation/fre.csv', '/home/user/.cache/inundation/dayflow.csv']
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        return []

    return sorted([str(f) for f in cache_dir.rglob("*") if f.is_file()])


def clear_cache() -> None:
    """Clear all cached inundation files.

    This function removes all cached files associated with the package.

    Examples
    --------
    >>> clear_cache()
    Removing existing cache.
    """
    cache_dir = get_cache_dir()
    files = list(cache_dir.rglob("*"))

    if len(files) > 0:
        print("Removing existing cache.")
        for f in files:
            if f.is_file():
                f.unlink()
    else:
        print("No cache to remove.")
