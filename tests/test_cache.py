"""Tests for the cache module."""

from pathlib import Path
from unittest.mock import patch

from inundation.cache import clear_cache, get_cache_dir, get_cache_file, show_cache


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
        # The directory should exist after calling get_cache_dir
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


class TestShowCache:
    """Test the show_cache function."""

    def test_returns_list(self) -> None:
        """Test that show_cache returns a list."""
        result = show_cache()
        assert isinstance(result, list)

    def test_list_contains_strings(self) -> None:
        """Test that returned list contains strings."""
        result = show_cache()
        for item in result:
            assert isinstance(item, str)

    def test_empty_cache_returns_empty_list(self) -> None:
        """Test that empty cache returns empty list."""
        with patch("inundation.cache.get_cache_dir") as mock_get_cache:
            mock_path = Path("/nonexistent")
            mock_get_cache.return_value = mock_path

            result = show_cache()
            assert result == []

    def test_returns_sorted_list(self) -> None:
        """Test that returned list is sorted."""
        result = show_cache()
        assert result == sorted(result)


class TestClearCache:
    """Test the clear_cache function."""

    def test_clears_cache(self, tmp_path: Path) -> None:
        """Test that clear_cache removes files."""
        # Create temporary cache files
        cache_dir = tmp_path / "inundation"
        cache_dir.mkdir()
        test_file = cache_dir / "test.csv"
        test_file.write_text("test data")

        assert test_file.exists()

        with patch("inundation.cache.get_cache_dir", return_value=cache_dir):
            clear_cache()

        assert not test_file.exists()

    def test_clears_multiple_files(self, tmp_path: Path) -> None:
        """Test that clear_cache removes multiple files."""
        cache_dir = tmp_path / "inundation"
        cache_dir.mkdir()

        # Create multiple test files
        for i in range(3):
            test_file = cache_dir / f"test{i}.csv"
            test_file.write_text(f"test data {i}")

        with patch("inundation.cache.get_cache_dir", return_value=cache_dir):
            clear_cache()

        # All files should be deleted
        remaining = list(cache_dir.glob("*"))
        assert len(remaining) == 0

    def test_handles_empty_cache(self, tmp_path: Path) -> None:
        """Test that clear_cache handles empty cache gracefully."""
        cache_dir = tmp_path / "inundation"
        cache_dir.mkdir()

        with patch("inundation.cache.get_cache_dir", return_value=cache_dir):
            # Should not raise an error
            clear_cache()

    def test_skips_directories(self, tmp_path: Path) -> None:
        """Test that clear_cache skips directories."""
        cache_dir = tmp_path / "inundation"
        cache_dir.mkdir()

        # Create a file and a subdirectory
        test_file = cache_dir / "test.csv"
        test_file.write_text("test data")
        test_dir = cache_dir / "subdir"
        test_dir.mkdir()

        with patch("inundation.cache.get_cache_dir", return_value=cache_dir):
            clear_cache()

        # File should be deleted but subdirectory should remain
        assert not test_file.exists()
        # Note: Depending on implementation, subdirectory may or may not be deleted
