"""
Manage files, find them or return a random file with a specific pattern.
Handles telegram files ID in a cache so we do not have to re-upload the same file
again and again to telegram servers. Stores file IDs in a dict in memory and persists
it to a JSON file stored in the user's config folder.
"""

import json
import logging
from pathlib import Path
from random import choice
from typing import Optional, Tuple

from ._folders import audio_folder, files_id_db

logger = logging.getLogger(__name__)

_files_id_cache: dict[str, str] = {}
civilizations_pattern = "[A-Z][a-z]*.mp3"
taunts_pattern = "[0-9][0-9] *.mp3"
audio_pattern = "*.wav"


def get_sound_list() -> list[str]:
    return [str(sound.stem) for sound in list(audio_folder.glob(audio_pattern))]


def get_civilization_files() -> list[Path]:
    return list(audio_folder.glob(civilizations_pattern))


def get_civilization_list() -> list[str]:
    return [str(civ.stem) for civ in get_civilization_files()]


def get_taunt_list() -> list[str]:
    return [str(taunt.stem) for taunt in list(audio_folder.glob(taunts_pattern))]


def _get_random_file(pattern: str) -> Tuple[Optional[Path], Optional[str]]:
    """Get a random file matching the pattern, checking cache first.

    Args:
        pattern: Glob pattern to match files (e.g., "*.wav", "[0-9][0-9] *.mp3")
        category: Category name for logging (e.g., "audio", "taunt", "civilization")

    Returns:
        (file_path, file_id) tuple where one of them will be None:
        - If cached: (None, file_id)
        - If new file: (file_path, None)
        - If no files: (None, None)
    """
    logger.debug(f"Getting random file with {pattern}")

    files = list(audio_folder.glob(pattern))
    if not files:
        logger.warning("No files found")
        return None, None

    selected = choice(files)
    logger.debug(f"Selected {selected}")

    # search in cache _files_id_cache if the file is present

    return selected, None


def get_random_audio() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 sound file."""
    logger.debug("Getting random sound")
    return _get_random_file(audio_pattern)


def get_random_taunt() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 taunt audio file."""
    logger.debug("Getting random taunt")
    return _get_random_file(taunts_pattern)


def get_random_civilization() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 civilization audio file."""
    logger.debug("Getting random civilization audio")
    return _get_random_file(civilizations_pattern)


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
