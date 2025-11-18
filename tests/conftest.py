"""Shared pytest fixtures for all tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from aoe2_telegram_bot._files_id_db import clear_file_id_db


@pytest.fixture(autouse=True)
def clean_cache():
    """Clean file ID cache before and after each test."""
    clear_file_id_db()
    yield
    clear_file_id_db()


@pytest.fixture
def temp_audio_folder(tmp_path, monkeypatch):
    """Create a temporary audio folder with test files.

    Creates:
        - test1.wav, test2.wav (audio quotes)
        - 01 taunt.mp3, 02 taunt.mp3 (taunts)
        - Britons.mp3, Celts.mp3 (civilizations)
    """
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()

    # Create test audio files
    (audio_dir / "test1.wav").write_text("fake audio 1")
    (audio_dir / "test2.wav").write_text("fake audio 2")
    (audio_dir / "01 taunt.mp3").write_text("taunt 1")
    (audio_dir / "02 taunt.mp3").write_text("taunt 2")
    (audio_dir / "Britons.mp3").write_text("britons")
    (audio_dir / "Celts.mp3").write_text("celts")

    # Patch the audio_folder
    from aoe2_telegram_bot import _folders

    monkeypatch.setattr(_folders, "audio_folder", audio_dir)

    return audio_dir


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_chat.id = 12345
    update.message.text = "/test"
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram Context object."""
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    context.bot.send_audio = AsyncMock()

    # Mock the audio message response
    audio_message = MagicMock()
    audio_message.audio.file_id = "test_file_id_12345"
    context.bot.send_audio.return_value = audio_message

    return context


@pytest.fixture
def mock_audio_caption(tmp_path, monkeypatch):
    """Create a temporary audio caption file."""
    caption_file = tmp_path / "caption.png"
    caption_file.write_bytes(b"fake image")

    from aoe2_telegram_bot import _folders

    monkeypatch.setattr(_folders, "audio_caption", caption_file)

    return caption_file
