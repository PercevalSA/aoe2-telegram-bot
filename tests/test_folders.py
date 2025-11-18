"""Tests for folder and path utilities."""

from pathlib import Path

from aoe2_telegram_bot._folders import audio_caption, audio_folder


def test_get_audio_folder():
    assert isinstance(audio_folder, Path)
    assert audio_folder.name == "audio"


def test_audio_folder_is_path():
    assert isinstance(audio_folder, Path)


def test_audio_caption_is_path():
    assert isinstance(audio_caption, Path)
    assert audio_caption.suffix == ".png"
