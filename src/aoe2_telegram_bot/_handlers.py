import logging
from pathlib import Path
from random import choice
from typing import Optional, Tuple

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from ._files_id_db import get_file_id, get_random_cached_file, set_file_id
from ._folders import audio_caption, audio_folder

logger = logging.getLogger(__name__)


def get_random_audio() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 quote audio file.

    Returns (file_path, file_id) tuple where one of them will be None:
    - If cached: (None, file_id)
    - If new file: (file_path, None)
    - If no files: (None, None)
    """
    logger.debug("Getting random audio")

    # First try to get from cache
    cached = get_random_cached_file("*.wav")
    if cached:
        filename, file_id = cached
        logger.debug(f"Using cached audio: {filename}")
        return None, file_id

    # No cached files, search filesystem
    logger.debug("No cached audio files, searching filesystem")
    audio_files = list(audio_folder.glob("*.wav"))

    if not audio_files:
        logger.warning("No audio files found")
        return None, None

    audio = choice(audio_files)
    logger.debug(f"Selected {audio}")
    return audio, None


def get_random_taunt() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 taunt audio file.

    Returns (file_path, file_id) tuple where one of them will be None:
    - If cached: (None, file_id)
    - If new file: (file_path, None)
    - If no files: (None, None)
    """
    logger.debug("Getting random taunt")

    # First try to get from cache
    cached = get_random_cached_file("[0-9][0-9] *.mp3")
    if cached:
        filename, file_id = cached
        logger.debug(f"Using cached taunt: {filename}")
        return None, file_id

    # No cached files, search filesystem
    logger.debug("No cached taunt files, searching filesystem")
    taunt_files = list(audio_folder.glob("[0-9][0-9] *.mp3"))

    if not taunt_files:
        logger.warning("No taunt files found")
        return None, None

    taunt = choice(taunt_files)
    logger.debug(f"Selected {taunt}")
    return taunt, None


def get_random_civilization() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 civilization audio file.

    Returns (file_path, file_id) tuple where one of them will be None:
    - If cached: (None, file_id)
    - If new file: (file_path, None)
    - If no files: (None, None)
    """
    logger.debug("Getting random civilization")

    # First try to get from cache
    cached = get_random_cached_file("civ_*.mp3")
    if cached:
        filename, file_id = cached
        logger.debug(f"Using cached civilization: {filename}")
        return None, file_id

    # No cached files, search filesystem
    logger.debug("No cached civilization files, searching filesystem")
    civ_files = list(audio_folder.glob("civ_*.mp3"))

    if not civ_files:
        logger.warning("No civilization files found")
        return None, None

    civilization = choice(civ_files)
    logger.debug(f"Selected {civilization}")
    return civilization, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="À la bataille! Use /aoe to get a quote from Age of Empires II.",
    )


async def send_audio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    audio_file: Optional[Path],
    file_id: Optional[str] = None,
):
    """Send an audio file to the user.

    Args:
        update: Telegram update
        context: Bot context
        audio_file: Path to audio file (if uploading new file)
        file_id: Telegram file_id (if using cached file)
    """
    # Handle case where both are None
    if audio_file is None and file_id is None:
        logger.error("No audio file or file_id provided")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, no audio files available.",
        )
        return

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.RECORD_VOICE,
    )

    # Determine what to send and optional title
    audio_to_send = file_id
    title = None

    if file_id:
        logger.debug(f"Using cached file_id: {file_id}")
    elif audio_file:
        # Check if we have a cached file_id for this file
        cached_file_id = get_file_id(audio_file)
        if cached_file_id:
            logger.debug(
                f"Using cached file_id for {audio_file.name}: {cached_file_id}"
            )
            audio_to_send = cached_file_id
        else:
            logger.debug(f"No cached file_id for {audio_file.name}, uploading file")
            audio_to_send = audio_file
        title = audio_file.stem
    else:
        logger.error("audio_file is None but no file_id provided")
        return

    # Single send_audio call
    message = await context.bot.send_audio(
        chat_id=update.effective_chat.id,
        audio=audio_to_send,
        title=title,
        thumbnail=audio_caption,
        disable_notification=True,
    )

    # Cache new file_id if we just uploaded
    if audio_file and not file_id and not get_file_id(audio_file):
        new_file_id = message.audio.file_id
        set_file_id(audio_file, new_file_id)
        logger.debug(f"Cached new file_id for {audio_file.name}: {new_file_id}")

    logger.info(f"Audio sent: {title or 'cached file'}")


async def send_sound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file, file_id = get_random_audio()
    await send_audio(update, context, audio_file, file_id)


async def send_civ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file, file_id = get_random_civilization()
    await send_audio(update, context, audio_file, file_id)


async def send_taunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file, file_id = get_random_taunt()
    await send_audio(update, context, audio_file, file_id)


async def taunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("searching for corresponding taunt")
    taunt_num = update.message.text.strip("/").zfill(2)
    taunt_file = list(audio_folder.glob(f"{taunt_num} *.mp3"))
    logger.debug(f"Taunt {taunt_num} found: {taunt_file}")

    if not taunt_file:
        logger.debug(f"Taunt {taunt_num} not found")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Taunt {taunt_num} not found",
        )
        return

    taunt = taunt_file[0]
    logger.debug(f"Sending taunt {taunt}")
    await send_audio(update, context, taunt)


def register_taunt_handlers(application: ApplicationBuilder):
    taunt_number: int = 42
    for i in range(1, taunt_number + 1):
        application.add_handler(CommandHandler(f"{i}", taunt))


def register_handlers(application: ApplicationBuilder):
    logger.info("Registering handlers")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("aoe", send_sound))
    application.add_handler(CommandHandler("civ", send_civ))
    application.add_handler(CommandHandler("taunt", send_taunt))

    register_taunt_handlers(application)
