"""Tests for folder and path utilities."""

from pathlib import Path

from aoe2_telegram_bot._folders import audio_caption, audio_folder, get_audio_folder


def test_get_audio_folder():
    """Test getting audio folder path."""
    folder = get_audio_folder()
    assert isinstance(folder, Path)
    assert folder.name == "audio"


def test_audio_folder_is_path():
    """Test that audio_folder is a Path object."""
    assert isinstance(audio_folder, Path)


def test_audio_caption_is_path():
    """Test that audio_caption is a Path object."""
    assert isinstance(audio_caption, Path)
    assert audio_caption.suffix == ".png"
