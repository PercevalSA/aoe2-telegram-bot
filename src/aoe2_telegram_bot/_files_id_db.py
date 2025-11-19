"""
Handles telegram files ID so we do not have to re-upload the same file again and again.
Stores file IDs in a dict in memory and persists it to a JSON file
stored in the user's config folder.
"""

import json
from pathlib import Path
from typing import Optional

from ._folders import files_id_db

_files_id_cache: dict[str, str] = {}


def load_cache() -> None:
    """Load cache from file if not already loaded. Called at startup."""
    if _files_id_cache or not files_id_db.exists():
        return

    try:
        with files_id_db.open("r") as f:
            _files_id_cache.update(json.load(f))
    except (json.JSONDecodeError, ValueError):
        pass  # Corrupted or empty file, start fresh


def get_file_id(file_path: Path) -> Optional[str]:
    """Get the telegram file ID for a given file path, or None if not found."""
    return _files_id_cache.get(file_path.name)


def set_file_id(file_path: Path, file_id: str) -> None:
    """Set the telegram file ID for a given file path."""
    _files_id_cache[file_path.name] = file_id
    # Write entire cache to file
    files_id_db.parent.mkdir(parents=True, exist_ok=True)
    with files_id_db.open("w") as f:
        json.dump(_files_id_cache, f, indent=2)


def clear_file_id_db() -> None:
    """Clear the file ID database."""
    _files_id_cache.clear()
    files_id_db.unlink(missing_ok=True)


def get_all_file_ids() -> dict[str, str]:
    """Get all file IDs in the database."""
    return _files_id_cache.copy()
