"""Tests for the cache module.

These tests verify the caching infrastructure including:
- Basic cache directory and file operations
- Request-aware caching (different params = different files)
- Cache metadata (index.json)
- Cache filtering (by dataset, age)
- show_cache() and clear_cache() functions
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from inundation.cache import (
    add_to_index,
    clear_cache,
    get_cache_dir,
    get_cache_file,
    get_cache_metadata,
    get_index_path,
    load_index,
    make_cache_key,
    matches_cache_request,
    save_index,
    show_cache,
)


class TestGetCacheDir:
    """Test the get_cache_dir function."""

    def test_returns_path_object(self) -> None:
        """Test that get_cache_dir returns a Path object."""
        result = get_cache_dir()
        assert isinstance(result, Path)

    def test_directory_contains_inundation(self) -> None:
        """Test that cache dir path contains 'inundation'."""
        result = get_cache_dir()
        assert "inundation" in str(result)

    def test_directory_is_created(self) -> None:
        """Test that directory is created if it doesn't exist."""
        cache_dir = get_cache_dir()
        assert cache_dir.exists()
        assert cache_dir.is_dir()


class TestGetCacheFile:
    """Test the get_cache_file function."""

    def test_returns_path_object(self) -> None:
        """Test that get_cache_file returns a Path object."""
        result = get_cache_file("test.csv")
        assert isinstance(result, Path)

    def test_path_ends_with_filename(self) -> None:
        """Test that returned path ends with the given filename."""
        filename = "test.csv"
        result = get_cache_file(filename)
        assert result.name == filename

    def test_path_contains_cache_dir(self) -> None:
        """Test that returned path is within the cache directory."""
        result = get_cache_file("test.csv")
        cache_dir = get_cache_dir()
        assert result.parent == cache_dir


class TestMakeCacheKey:
    """Test the make_cache_key function for human-readable filenames."""

    def test_no_params_returns_simple_filename(self) -> None:
        """Test that no params produces a simple filename."""
        result = make_cache_key("dayflow", {})
        assert result == "dayflow.csv"

    def test_single_param(self) -> None:
        """Test single parameter produces readable filename."""
        result = make_cache_key("fre", {"station_id": "FRE"})
        assert result == "fre_FRE.csv"

    def test_multiple_params_sorted(self) -> None:
        """Test multiple parameters are sorted alphabetically for consistency."""
        result = make_cache_key(
            "fre", {"station_id": "FRE", "start": "2020-01-01", "end": "2020-12-31"}
        )
        # Should be sorted: end, start, station_id
        assert result == "fre_2020-12-31_2020-01-01_FRE.csv"

    def test_none_values_excluded(self) -> None:
        """Test that None values are excluded from filename."""
        result = make_cache_key("fre", {"station_id": "FRE", "end": None})
        assert "None" not in result
        assert result == "fre_FRE.csv"

    def test_special_characters_sanitized(self) -> None:
        """Test that filenames don't have problematic characters."""
        result = make_cache_key("test", {"param": "has/slash and spaces"})
        # Slashes become hyphens, spaces become underscores
        assert "/" not in result
        assert " " not in result


class TestIndexOperations:
    """Test the cache index file operations."""

    def test_load_index_empty_returns_dict(self, tmp_path: Path) -> None:
        """Test that loading an empty/nonexistent index returns empty dict."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            result = load_index()
            assert result == {}

    def test_save_and_load_index(self, tmp_path: Path) -> None:
        """Test saving and loading the index."""
        test_data = {
            "test.csv": {
                "params": {"station_id": "FRE"},
                "source_url": "http://example.com",
                "downloaded_at": "2025-01-01T00:00:00",
                "row_count": 100,
            }
        }

        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            save_index(test_data)
            loaded = load_index()
            assert loaded == test_data

    def test_corrupted_index_returns_empty(self, tmp_path: Path) -> None:
        """Test that corrupted JSON returns empty dict instead of crashing."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Write invalid JSON
            index_path = get_index_path()
            index_path.write_text("not valid json {{{")

            result = load_index()
            assert result == {}


class TestAddToIndex:
    """Test adding entries to the cache index."""

    def test_add_new_entry(self, tmp_path: Path) -> None:
        """Test adding a new cache entry to the index."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create a fake cache file
            cache_file = tmp_path / "test.csv"
            cache_file.write_text("data,more\n1,2\n3,4")

            add_to_index(
                filename="test.csv",
                params={"station": "FRE"},
                source_url="http://example.com",
                row_count=2,
            )

            index = load_index()
            assert "test.csv" in index
            assert index["test.csv"]["params"] == {"station": "FRE"}
            assert index["test.csv"]["source_url"] == "http://example.com"
            assert index["test.csv"]["row_count"] == 2
            assert "downloaded_at" in index["test.csv"]
            assert "package_version" in index["test.csv"]

    def test_update_existing_entry(self, tmp_path: Path) -> None:
        """Test that adding the same filename updates the entry."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            cache_file = tmp_path / "test.csv"
            cache_file.write_text("data\n1")

            # Add first time
            add_to_index(
                filename="test.csv",
                params={"v": 1},
                source_url="http://old.com",
                row_count=1,
            )

            # Add second time (update)
            add_to_index(
                filename="test.csv",
                params={"v": 2},
                source_url="http://new.com",
                row_count=10,
            )

            index = load_index()
            assert index["test.csv"]["params"] == {"v": 2}
            assert index["test.csv"]["source_url"] == "http://new.com"
            assert index["test.csv"]["row_count"] == 10


class TestMatchesCacheRequest:
    """Test the matches_cache_request function."""

    def test_matches_when_params_equal(self, tmp_path: Path) -> None:
        """Test that matching params return True."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            cache_file = tmp_path / "test.csv"
            cache_file.write_text("data")

            params = {"station": "FRE", "start": "2020-01-01"}
            add_to_index("test.csv", params, "http://example.com", 1)

            assert matches_cache_request("test.csv", params) is True

    def test_no_match_for_different_params(self, tmp_path: Path) -> None:
        """Test that different params return False."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            cache_file = tmp_path / "test.csv"
            cache_file.write_text("data")

            add_to_index("test.csv", {"station": "FRE"}, "http://example.com", 1)

            assert matches_cache_request("test.csv", {"station": "DIFFERENT"}) is False

    def test_no_match_when_no_metadata(self, tmp_path: Path) -> None:
        """Test that missing metadata returns False."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            assert matches_cache_request("nonexistent.csv", {}) is False


class TestShowCache:
    """Test the show_cache function."""

    def test_returns_list(self, tmp_path: Path) -> None:
        """Test that show_cache returns a list."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            result = show_cache()
            assert isinstance(result, list)

    def test_empty_cache_returns_empty_list(self, tmp_path: Path) -> None:
        """Test that empty cache directory returns empty list."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            result = show_cache()
            assert result == []

    def test_returns_metadata_dictionary(self, tmp_path: Path) -> None:
        """Test that show_cache returns rich metadata dictionaries."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create cache file with metadata
            cache_file = tmp_path / "test.csv"
            cache_file.write_text("col1,col2\n1,2")

            add_to_index(
                filename="test.csv",
                params={"station": "FRE"},
                source_url="http://example.com",
                row_count=1,
            )

            result = show_cache()
            assert len(result) == 1
            entry = result[0]

            # Check all expected fields are present
            assert entry["filename"] == "test.csv"
            assert entry["source_url"] == "http://example.com"
            assert "downloaded_at" in entry
            assert entry["row_count"] == 1
            assert "file_size_bytes" in entry
            assert entry["params"] == {"station": "FRE"}
            assert "package_version" in entry

    def test_handles_files_without_metadata(self, tmp_path: Path) -> None:
        """Test files without index metadata still appear (with defaults)."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create cache file WITHOUT adding to index
            cache_file = tmp_path / "orphan.csv"
            cache_file.write_text("data\n1")

            result = show_cache()
            assert len(result) == 1
            entry = result[0]
            assert entry["filename"] == "orphan.csv"
            assert entry["source_url"] == "unknown"
            assert entry["row_count"] == 0


class TestClearCache:
    """Test the clear_cache function with filtering options."""

    def test_clears_all_when_no_filter(self, tmp_path: Path) -> None:
        """Test that clear_cache() with no filter removes all caches."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create multiple cache files
            for name in ["fre_test.csv", "dayflow.csv", "other.csv"]:
                (tmp_path / name).write_text("data")

            removed = clear_cache()
            assert removed == 3
            assert len(list(tmp_path.glob("*.csv"))) == 0

    def test_clears_only_dataset_filter(self, tmp_path: Path) -> None:
        """Test filtering by dataset prefix."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create cache files with different prefixes
            (tmp_path / "fre_2020.csv").write_text("data")
            (tmp_path / "fre_2021.csv").write_text("data")
            (tmp_path / "dayflow.csv").write_text("data")

            # Clear only fre_*
            removed = clear_cache(dataset="fre")
            assert removed == 2

            # dayflow.csv should still exist
            remaining = list(tmp_path.glob("*.csv"))
            assert len(remaining) == 1
            assert remaining[0].name == "dayflow.csv"

    def test_clears_by_age_filter(self, tmp_path: Path) -> None:
        """Test filtering by age in days."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create old cache with old metadata
            old_file = tmp_path / "old.csv"
            old_file.write_text("data")
            old_date = (datetime.now() - timedelta(days=30)).isoformat()
            save_index(
                {
                    "old.csv": {
                        "params": {},
                        "source_url": "http://example.com",
                        "downloaded_at": old_date,
                        "row_count": 1,
                    }
                }
            )

            # Create recent cache
            recent_file = tmp_path / "recent.csv"
            recent_file.write_text("data")
            recent_date = datetime.now().isoformat()

            # Re-load and add recent
            index = load_index()
            index["recent.csv"] = {
                "params": {},
                "source_url": "http://example.com",
                "downloaded_at": recent_date,
                "row_count": 1,
            }
            save_index(index)

            # Clear caches older than 7 days
            removed = clear_cache(older_than_days=7)
            assert removed == 1

            # Old should be gone, recent should remain
            assert not old_file.exists()
            assert recent_file.exists()

    def test_clears_with_combined_filters(self, tmp_path: Path) -> None:
        """Test combining dataset and age filters."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            # Create various cache files
            old_date = (datetime.now() - timedelta(days=30)).isoformat()
            recent_date = datetime.now().isoformat()

            files = {
                "fre_old.csv": {"date": old_date},
                "fre_new.csv": {"date": recent_date},
                "dayflow.csv": {"date": old_date},
            }

            index = {}
            for filename, info in files.items():
                (tmp_path / filename).write_text("data")
                index[filename] = {
                    "params": {},
                    "source_url": "http://example.com",
                    "downloaded_at": info["date"],
                    "row_count": 1,
                }
            save_index(index)

            # Clear only old fre_* files
            removed = clear_cache(dataset="fre", older_than_days=7)
            assert removed == 1

            # Only fre_old.csv should be removed
            assert not (tmp_path / "fre_old.csv").exists()
            assert (tmp_path / "fre_new.csv").exists()
            assert (tmp_path / "dayflow.csv").exists()

    def test_handles_empty_cache(self, tmp_path: Path) -> None:
        """Test that clear_cache handles empty cache gracefully."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            removed = clear_cache()
            assert removed == 0

    def test_returns_count_of_removed_files(self, tmp_path: Path) -> None:
        """Test that clear_cache returns the count of removed files."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            for i in range(5):
                (tmp_path / f"test{i}.csv").write_text("data")

            removed = clear_cache()
            assert removed == 5


class TestGetCacheMetadata:
    """Test the get_cache_metadata function."""

    def test_returns_metadata_when_exists(self, tmp_path: Path) -> None:
        """Test retrieving metadata for existing cache."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            cache_file = tmp_path / "test.csv"
            cache_file.write_text("data")

            params = {"station": "FRE"}
            add_to_index("test.csv", params, "http://example.com", 1)

            metadata = get_cache_metadata("test.csv")
            assert metadata is not None
            assert metadata["params"] == params

    def test_returns_none_when_not_exists(self, tmp_path: Path) -> None:
        """Test that missing entry returns None."""
        with patch("inundation.cache.get_cache_dir", return_value=tmp_path):
            metadata = get_cache_metadata("nonexistent.csv")
            assert metadata is None
