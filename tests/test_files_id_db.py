"""Tests for file ID database functionality."""

from aoe2_telegram_bot._files_id_db import (
    clear_file_id_db,
    get_all_file_ids,
    get_file_id,
    load_cache,
    set_file_id,
)


def test_set_and_get_file_id(tmp_path):
    """Test setting and retrieving file IDs."""
    test_file = tmp_path / "test.wav"
    test_file.touch()

    set_file_id(test_file, "file_id_123")

    result = get_file_id(test_file)
    assert result == "file_id_123"


def test_get_file_id_not_found(tmp_path):
    """Test getting a file ID that doesn't exist."""
    test_file = tmp_path / "nonexistent.wav"

    result = get_file_id(test_file)
    assert result is None


def test_get_all_file_ids(tmp_path):
    """Test retrieving all file IDs."""
    file1 = tmp_path / "test1.wav"
    file2 = tmp_path / "test2.wav"
    file1.touch()
    file2.touch()

    set_file_id(file1, "id_1")
    set_file_id(file2, "id_2")

    all_ids = get_all_file_ids()
    assert len(all_ids) == 2
    assert "test1.wav" in all_ids
    assert "test2.wav" in all_ids
    assert all_ids["test1.wav"] == "id_1"
    assert all_ids["test2.wav"] == "id_2"


def test_clear_file_id_db(tmp_path):
    """Test clearing the file ID database."""
    test_file = tmp_path / "test.wav"
    test_file.touch()

    set_file_id(test_file, "file_id_123")
    assert get_file_id(test_file) == "file_id_123"

    clear_file_id_db()
    assert get_file_id(test_file) is None


def test_load_cache_empty_file(tmp_path, monkeypatch):
    """Test loading cache when file doesn't exist."""
    from aoe2_telegram_bot import _folders

    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr(_folders, "files_id_db", cache_file)

    clear_file_id_db()
    load_cache()

    all_ids = get_all_file_ids()
    assert len(all_ids) == 0


def test_cache_persistence(tmp_path, monkeypatch):
    """Test that cache persists to disk."""
    from aoe2_telegram_bot import _files_id_db
    from aoe2_telegram_bot._files_id_db import _files_id_cache

    cache_file = tmp_path / "cache.json"
    # Patch files_id_db in the _files_id_db module itself
    monkeypatch.setattr(_files_id_db, "files_id_db", cache_file)

    # Start with empty cache
    _files_id_cache.clear()

    # Set a file ID (should write to disk)
    test_file = tmp_path / "test.wav"
    test_file.touch()
    set_file_id(test_file, "persisted_id")

    # Verify file was created
    assert cache_file.exists(), f"Cache file should exist at {cache_file}"

    # Clear in-memory cache only (not the file) and reload
    _files_id_cache.clear()

    # Force load from disk by checking the file exists first
    assert cache_file.exists(), "Cache file was deleted unexpectedly"
    load_cache()

    # Should have loaded from disk
    result = get_file_id(test_file)
    assert result == "persisted_id", f"Expected 'persisted_id', got {result}"


def test_load_cache_with_corrupted_json(tmp_path, monkeypatch):
    """Test loading cache when JSON file is corrupted."""
    from aoe2_telegram_bot import _files_id_db
    from aoe2_telegram_bot._files_id_db import _files_id_cache

    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr(_files_id_db, "files_id_db", cache_file)

    # Write corrupted JSON to file
    cache_file.write_text("{invalid json content")

    # Clear cache and try to load corrupted file
    _files_id_cache.clear()
    load_cache()  # Should not raise exception

    # Cache should be empty after failing to load
    all_ids = get_all_file_ids()
    assert len(all_ids) == 0
