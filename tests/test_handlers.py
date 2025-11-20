"""Tests for handler functions."""

import pytest

from aoe2_telegram_bot._files_id_db import set_file_id
from aoe2_telegram_bot._handlers import (
    _get_random_file,
    civilization,
    get_random_audio,
    get_random_civilization,
    get_random_taunt,
    help_command,
    list_civilizations,
    send_audio,
    send_civ,
    send_sound,
    send_taunt,
    start,
    taunt,
    unknown_command,
)


def test_get_random_file_from_filesystem(temp_audio_folder):
    """Test getting random file from filesystem when cache is empty."""
    file_path, file_id = _get_random_file("*.wav", "audio")

    assert file_path is not None
    assert file_path.suffix == ".wav"
    assert file_path.name in ["test1.wav", "test2.wav"]
    assert file_id is None


def test_get_random_file_no_files(tmp_path, monkeypatch):
    """Test getting random file when no files exist."""
    from aoe2_telegram_bot import _folders

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    monkeypatch.setattr(_folders, "audio_folder", empty_dir)

    file_path, file_id = _get_random_file("*.wav", "audio")

    assert file_path is None
    assert file_id is None


def test_get_random_audio(temp_audio_folder):
    """Test getting random audio quote."""
    file_path, file_id = get_random_audio()

    assert file_path is not None
    assert file_path.suffix == ".wav"


def test_get_random_taunt(temp_audio_folder):
    """Test getting random taunt."""
    file_path, file_id = get_random_taunt()

    assert file_path is not None
    assert file_path.suffix == ".mp3"
    assert file_path.name.startswith(("01", "02"))


def test_get_random_civilization(temp_audio_folder):
    """Test getting random civilization."""
    file_path, file_id = get_random_civilization()

    assert file_path is not None
    assert file_path.suffix == ".mp3"
    assert file_path.name in ["Britons.mp3", "Celts.mp3"]


@pytest.mark.asyncio
async def test_send_audio_new_file(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test sending a new audio file (not in cache)."""
    from aoe2_telegram_bot._files_id_db import get_file_id

    audio_file = temp_audio_folder / "test1.wav"

    await send_audio(mock_update, mock_context, audio_file, None)

    # Should have sent the audio
    mock_context.bot.send_audio.assert_called_once()
    call_kwargs = mock_context.bot.send_audio.call_args.kwargs
    assert call_kwargs["audio"] == audio_file
    assert call_kwargs["title"] == "test1"

    # Should have cached the file_id
    cached_id = get_file_id(audio_file)
    assert cached_id == "test_file_id_12345"


@pytest.mark.asyncio
async def test_send_audio_cached_file_id(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test sending audio using cached file_id."""
    cached_id = "existing_cached_id"

    await send_audio(mock_update, mock_context, None, cached_id)

    # Should send using file_id
    mock_context.bot.send_audio.assert_called_once()
    call_kwargs = mock_context.bot.send_audio.call_args.kwargs
    assert call_kwargs["audio"] == cached_id
    assert call_kwargs.get("title") is None  # No title for cached IDs


@pytest.mark.asyncio
async def test_send_audio_with_existing_cache(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test sending audio when file already has cached ID."""
    audio_file = temp_audio_folder / "test1.wav"
    cached_id = "pre_existing_id"
    set_file_id(audio_file, cached_id)

    await send_audio(mock_update, mock_context, audio_file, None)

    # Should use cached ID instead of uploading
    mock_context.bot.send_audio.assert_called_once()
    call_kwargs = mock_context.bot.send_audio.call_args.kwargs
    assert call_kwargs["audio"] == cached_id


@pytest.mark.asyncio
async def test_send_audio_no_file_no_id(mock_update, mock_context, mock_audio_caption):
    """Test error handling when neither file nor file_id provided."""
    await send_audio(mock_update, mock_context, None, None)

    # Should send error message
    mock_context.bot.send_message.assert_called_once()
    assert (
        "no audio files available"
        in mock_context.bot.send_message.call_args.kwargs["text"].lower()
    )


@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """Test start command."""
    await start(mock_update, mock_context)

    mock_context.bot.send_message.assert_called_once()
    call_kwargs = mock_context.bot.send_message.call_args.kwargs
    assert (
        "bienvenue" in call_kwargs["text"].lower()
        or "welcome" in call_kwargs["text"].lower()
    )


@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    """Test help command."""
    await help_command(mock_update, mock_context)

    mock_context.bot.send_message.assert_called_once()
    call_kwargs = mock_context.bot.send_message.call_args.kwargs
    assert (
        "aoe" in call_kwargs["text"].lower()
        or "commands" in call_kwargs["text"].lower()
    )


@pytest.mark.asyncio
async def test_unknown_command(mock_update, mock_context):
    """Test unknown command handler."""
    await unknown_command(mock_update, mock_context)

    mock_context.bot.send_message.assert_called_once()
    call_kwargs = mock_context.bot.send_message.call_args.kwargs
    assert "unknown" in call_kwargs["text"].lower()


@pytest.mark.asyncio
async def test_send_sound(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test send_sound command."""
    await send_sound(mock_update, mock_context)

    # Should have sent audio
    mock_context.bot.send_audio.assert_called_once()


@pytest.mark.asyncio
async def test_send_civ(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test send_civ command."""
    await send_civ(mock_update, mock_context)

    # Should have sent audio
    mock_context.bot.send_audio.assert_called_once()


@pytest.mark.asyncio
async def test_send_taunt_command(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test send_taunt command."""
    await send_taunt(mock_update, mock_context)

    # Should have sent audio
    mock_context.bot.send_audio.assert_called_once()


@pytest.mark.asyncio
async def test_taunt_specific_number(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test taunt command with specific number."""
    mock_update.message.text = "/11"

    # Create taunt file
    taunt_file = temp_audio_folder / "11 wololo.mp3"
    taunt_file.write_text("fake taunt")

    await taunt(mock_update, mock_context)

    # Should have sent audio
    mock_context.bot.send_audio.assert_called_once()


@pytest.mark.asyncio
async def test_taunt_not_found(temp_audio_folder, mock_update, mock_context):
    """Test taunt command when taunt doesn't exist."""
    mock_update.message.text = "/99"

    await taunt(mock_update, mock_context)

    # Should send error message
    mock_context.bot.send_message.assert_called_once()
    call_kwargs = mock_context.bot.send_message.call_args.kwargs
    assert "not found" in call_kwargs["text"].lower()


@pytest.mark.asyncio
async def test_civilization_specific(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test civilization command with specific civ."""
    mock_update.message.text = "/britons"

    await civilization(mock_update, mock_context)

    # Should have sent audio
    mock_context.bot.send_audio.assert_called_once()


@pytest.mark.asyncio
async def test_civilization_case_insensitive(
    temp_audio_folder, mock_update, mock_context, mock_audio_caption
):
    """Test civilization command is case insensitive."""
    mock_update.message.text = "/BRITONS"

    await civilization(mock_update, mock_context)

    # Should have sent audio
    mock_context.bot.send_audio.assert_called_once()


@pytest.mark.asyncio
async def test_civilization_not_found(temp_audio_folder, mock_update, mock_context):
    """Test civilization command when civ doesn't exist."""
    mock_update.message.text = "/atlantis"

    await civilization(mock_update, mock_context)

    # Should send error message
    mock_context.bot.send_message.assert_called_once()
    call_kwargs = mock_context.bot.send_message.call_args.kwargs
    assert "not found" in call_kwargs["text"].lower()


@pytest.mark.asyncio
async def test_list_civilizations(temp_audio_folder, mock_update, mock_context):
    """Test list civilizations command."""
    await list_civilizations(mock_update, mock_context)

    mock_context.bot.send_message.assert_called_once()
    call_kwargs = mock_context.bot.send_message.call_args.kwargs
    text = call_kwargs["text"]
    # Should contain civilization names with slashes
    assert "/britons" in text.lower() or "/celts" in text.lower()
