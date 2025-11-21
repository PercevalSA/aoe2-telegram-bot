"""Handler functions for Telegram bot commands."""

import logging
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ._files import (
    get_civilization_list,
    get_file_id,
    get_sound_list,
    get_taunt_list,
    set_file_id,
)
from ._folders import audio_caption, audio_folder

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "🏰 *Bienvenue sur le bot Sound Box Age of Empires II!* ⚔️\n\n"
            "utilisez /aide pour la liste des commandes.\n"
            "use /help for the list of commands.\n\n"
            "Vous pouvez aussi utiliser /start pour revenir à ce message."
            "You can also use /start to return here."
        ),
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display help message with available commands in english"""
    en = """
🏰 *Age of Empires II Bot* 🎮

*Random Audio Commands:*
/sound - Get a random AoE2 quote
/taunt - Get a random taunt
/civilization - Get a random civilization sound

*Specific Commands:*
/1 to /42 - Get a specific taunt by number
    _Example: /11 for "11"_
/britons, /celts, /vikings, etc. - Get a specific civilization sound
    _Example: /britons_

*List Commands:*
/taunts - Show all available taunts
/civilizations - Show all available civilizations
/sounds - Show all available sounds

*Help:*
/help - Show this help message (English)
/start - Welcome message

à la bataille! ⚔️
"""

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=en, parse_mode="Markdown"
    )


async def help_command_french(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display help message with available commands in french"""
    fr = """
🏰 *Bot Age of Empires II* 🎮

*Commandes audio aléatoires :*
/bruitage - Obtenir un son aléatoire de AoE2 
/provocation - Obtenir une provocation aléatoire
/civilisation - Obtenir un son de civilisation aléatoire

*Commandes spécifiques :*
/1 à /42 - Obtenir une provocation spécifique par numéro
/britons, /celts, /vikings, etc. - Obtenir un son de civilisation spécifique

*Commandes de listes :*
/provocations - Afficher toutes les provocations disponibles
/civilisations - Afficher toutes les civilisations disponibles
/bruits - Afficher tous les sons disponibles

*Aide :*
/aide - Afficher ce message d'aide (Français)
/start - Message de bienvenue

à la bataille ! ⚔️
"""

    logger.warning(f"sending french help message: {fr[600:610]}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=fr, parse_mode="Markdown"
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Unknown command. Use /help to see available commands.\n"
        "Commande inconnue. Utilisez /aide pour voir les commandes disponibles.",
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
    all_civs = get_civilization_list()
    civ_file = [civ for civ in all_civs if civ.lower() == civ_name.lower()]
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


async def list_civilizations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    civ_list = "\n".join(f"/{civ}" for civ in get_civilization_list())
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Available civilizations:\n{civ_list}",
    )


async def list_taunts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available taunts."""
    taunts = get_taunt_list()
    if not taunts:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No taunts available.",
        )
        return

    # Format as numbered list with command
    taunt_list = "\n".join(
        f"/{t.split()[0]}: {' '.join(t.split()[1:])}"
        for t in taunts
        if t.split()[0].isdigit()
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Available taunts:\n{taunt_list}",
    )


async def list_sounds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available sound files."""
    sounds = get_sound_list()
    if not sounds:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No sounds available.",
        )
        return

    sound_list = "\n".join(sounds)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Available sounds ({len(sounds)} files):\n{sound_list}",
    )


def register_taunt_handlers(application: ApplicationBuilder):
    """Register handlers for all taunt numbers dynamically based on available files."""
    taunt_numbers = set()
    for taunt_file in get_taunt_list():
        # Extract number from filename (e.g., "01 start the game.mp3" -> "1")
        parts = taunt_file.split()
        if parts and parts[0].isdigit():
            taunt_numbers.add(int(parts[0]))

    for taunt_num in sorted(taunt_numbers):
        application.add_handler(CommandHandler(str(taunt_num), taunt))


def register_civilization_handlers(application: ApplicationBuilder):
    """Register handlers for all civilizations dynamically."""
    for civ_name in get_civilization_list():
        # Register with lowercase to allow commands without capitals
        application.add_handler(CommandHandler(civ_name, civilization))
        application.add_handler(CommandHandler(civ_name.lower(), civilization))


# def register_sounds_handlers(application: ApplicationBuilder):


def register_handlers(application: ApplicationBuilder):
    """Register all bot handlers."""
    logger.debug("Registering handlers")

    handlers = {
        "start": start,
        "help": help_command,
        "aide": help_command_french,
        "sound": send_sound,
        "bruitage": send_sound,
        "civilization": send_civ,
        "civilisation": send_civ,
        "taunt": send_taunt,
        "provocation": send_taunt,
        "sounds": list_sounds,
        "bruits": list_sounds,
        "civilizations": list_civilizations,
        "civilisations": list_civilizations,
        "taunts": list_taunts,
        "provocations": list_taunts,
    }

    for command, function in handlers.items():
        application.add_handler(CommandHandler(command, function))

    register_taunt_handlers(application)
    register_civilization_handlers(application)

    # Unknown command handler must be registered last
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
