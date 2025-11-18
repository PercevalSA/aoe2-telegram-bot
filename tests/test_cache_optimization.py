#!/usr/bin/env python3
"""
Simple test to verify cache-first file selection optimization.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aoe2_telegram_bot._files_id_db import (
    _files_id_cache,
    clear_file_id_db,
    get_random_cached_file,
)


def test_cache_optimization():
    """Test that get_random_cached_file works correctly."""

    # Clear cache first
    clear_file_id_db()
    print("✓ Cache cleared")

    # Add some test files
    test_files = [
        ("quote1.wav", "file_id_1"),
        ("quote2.wav", "file_id_2"),
        ("01 taunt.mp3", "file_id_3"),
        ("02 taunt.mp3", "file_id_4"),
        ("Britons.mp3", "file_id_5"),
        ("Celts.mp3", "file_id_6"),
    ]

    for filename, file_id in test_files:
        _files_id_cache[filename] = file_id

    print(f"✓ Added {len(test_files)} test files to cache")

    # Test getting random audio files
    print("\nTesting audio pattern (*.wav):")
    for i in range(3):
        result = get_random_cached_file("*.wav")
        if result:
            filename, file_id = result
            print(f"  {i + 1}. Got: {filename} -> {file_id}")
            assert filename in ["quote1.wav", "quote2.wav"]
            assert file_id in ["file_id_1", "file_id_2"]
        else:
            print("  ERROR: No match found")
            sys.exit(1)

    # Test getting random taunts
    print("\nTesting taunt pattern ([0-9][0-9] *.mp3):")
    for i in range(3):
        result = get_random_cached_file("[0-9][0-9] *.mp3")
        if result:
            filename, file_id = result
            print(f"  {i + 1}. Got: {filename} -> {file_id}")
            assert filename in ["01 taunt.mp3", "02 taunt.mp3"]
            assert file_id in ["file_id_3", "file_id_4"]
        else:
            print("  ERROR: No match found")
            sys.exit(1)

    # Test getting random civilizations
    print("\nTesting civilization pattern ([A-Z][a-z]*.mp3):")
    for i in range(3):
        result = get_random_cached_file("[A-Z][a-z]*.mp3")
        if result:
            filename, file_id = result
            print(f"  {i + 1}. Got: {filename} -> {file_id}")
            assert filename in ["Britons.mp3", "Celts.mp3"]
            assert file_id in ["file_id_5", "file_id_6"]
        else:
            print("  ERROR: No match found")
            sys.exit(1)

    # Test with non-matching pattern
    print("\nTesting non-matching pattern (*.txt):")
    result = get_random_cached_file("*.txt")
    if result is None:
        print("  ✓ Correctly returned None for non-matching pattern")
    else:
        print(f"  ERROR: Expected None, got {result}")
        sys.exit(1)

    # Clean up
    clear_file_id_db()
    print("\n✓ Cache cleared after test")

    print("\n✅ All tests passed! Cache optimization is working correctly.")


if __name__ == "__main__":
    test_cache_optimization()
