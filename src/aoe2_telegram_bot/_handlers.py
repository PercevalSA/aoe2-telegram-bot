import logging
from pathlib import Path
from random import choice
from typing import Optional, Tuple

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ._files_id_db import get_file_id, set_file_id
from ._folders import (
    audio_caption,
    audio_folder,
    audio_pattern,
    civilizations_pattern,
    taunts_pattern,
)

logger = logging.getLogger(__name__)


def _get_random_file(
    pattern: str, category: str
) -> Tuple[Optional[Path], Optional[str]]:
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
    logger.debug(f"Getting random {category}")

    # No cached files, search filesystem
    logger.debug(f"No cached {category} files, searching filesystem")
    files = list(audio_folder.glob(pattern))
    if not files:
        logger.warning(f"No {category} files found")
        return None, None

    selected = choice(files)
    logger.debug(f"Selected {selected}")

    return selected, None


def get_random_audio() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 quote audio file."""
    return _get_random_file(audio_pattern, "audio")


def get_random_taunt() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 taunt audio file."""
    return _get_random_file(taunts_pattern, "taunt")


def get_random_civilization() -> Tuple[Optional[Path], Optional[str]]:
    """Return a random AoE2 civilization audio file."""
    return _get_random_file(civilizations_pattern, "civilization")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🏰 *Bienvenue sur le bot Age of Empires II!* ⚔️\n\n"
        "À la bataille! Utilisez /aide pour voir toutes les commandes disponibles.\n\n"
        "Welcome! Use /help to see all available commands.",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display help message with available commands."""
    help_text = """
🏰 *Age of Empires II Bot* 🎮

*Random Audio Commands:*
/sound, /bruit, /bruitage - Get a random AoE2 quote
/taunt, /provoc, /provocation - Get a random taunt
/civ, /civilisation - Get a random civilization sound

*Specific Commands:*
/1 to /42 - Get a specific taunt by number
  _Example: /11 for "11"_
/britons, /celts, /vikings, etc. - Get a specific civilization sound
  _Example: /britons_

*List Commands:*
/list, /liste - Show all available civilizations

*Help:*
/help, /aide - Show this help message
/start - Welcome message

À la bataille! ⚔️
"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode="Markdown",
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Unknown command. Use /help to see available commands.",
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


async def _send_random_audio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    get_file_func,
):
    """Helper to send a random audio file using the provided getter function."""
    audio_file, file_id = get_file_func()
    await send_audio(update, context, audio_file, file_id)


async def send_sound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_random_audio(update, context, get_random_audio)


async def send_civ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_random_audio(update, context, get_random_civilization)


async def send_taunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _send_random_audio(update, context, get_random_taunt)


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


async def civilization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    civ_name = update.message.text.strip("/")
    # Try case-insensitive search by checking all files
    all_civs = list(audio_folder.glob(civilizations_pattern))
    civ_file = [civ for civ in all_civs if civ.stem.lower() == civ_name.lower()]
    logger.debug(f"Civilization {civ_name} found: {civ_file}")

    if not civ_file:
        logger.debug(f"Civilization {civ_name} not found")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Civilization {civ_name} not found",
        )
        return

    civ = civ_file[0]
    logger.debug(f"Sending civilization {civ}")
    await send_audio(update, context, civ)


def register_taunt_handlers(application: ApplicationBuilder):
    taunt_number: int = 42
    for i in range(1, taunt_number + 1):
        application.add_handler(CommandHandler(f"{i}", taunt))


def _get_civilization_list() -> list[str]:
    return [str(civ.stem) for civ in list(audio_folder.glob(civilizations_pattern))]


def register_civilization_handlers(application: ApplicationBuilder):
    for civ_name in _get_civilization_list():
        # Register with lowercase to allow commands without capitals
        application.add_handler(CommandHandler(civ_name.lower(), civilization))


async def list_civilizations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    civ_list = "\n".join(f"/{civ}" for civ in _get_civilization_list())
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Available civilizations:\n{civ_list}",
    )


def register_handlers(application: ApplicationBuilder):
    logger.info("Registering handlers")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("aide", help_command))
    application.add_handler(CommandHandler("sound", send_sound))
    application.add_handler(CommandHandler("bruit", send_sound))
    application.add_handler(CommandHandler("bruitage", send_sound))
    application.add_handler(CommandHandler("civ", send_civ))
    application.add_handler(CommandHandler("civilisation", send_civ))
    application.add_handler(CommandHandler("list", list_civilizations))
    application.add_handler(CommandHandler("liste", list_civilizations))
    application.add_handler(CommandHandler("taunt", send_taunt))
    application.add_handler(CommandHandler("provoc", send_taunt))
    application.add_handler(CommandHandler("provocation", send_taunt))

    register_taunt_handlers(application)
    register_civilization_handlers(application)

    # Unknown command handler must be registered last
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
