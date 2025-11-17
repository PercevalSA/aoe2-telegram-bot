import logging
from pathlib import Path
from random import choice

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from ._folders import audio_caption, audio_folder

logger = logging.getLogger(__name__)


def get_random_audio() -> Path:
    """Return a random AoE2 quote audio file."""
    logger.debug("Getting random audio")
    audio = choice(list(audio_folder.glob("*.wav")))
    logger.debug(f"Selected {audio}")
    return audio


def get_random_taunt() -> Path:
    """Return a random AoE2 taunt audio file."""
    logger.debug("Getting random taunt")
    taunt = choice(list(audio_folder.glob("[0-9][0-9] *.mp3")))
    logger.debug(f"Selected {taunt}")
    return taunt


def get_random_civilization() -> Path:
    """Return a random AoE2 civilization audio file."""
    logger.debug("Getting random civilization")
    civilization = choice(list(audio_folder.glob("[A-Z]*.mp3")))
    logger.debug(f"Selected {civilization}")
    return civilization


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="À la bataille! Use /aoe to get a quote from Age of Empires II.",
    )


async def send_audio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    audio_file: Path,
):
    logger.debug(f"sending audio file {audio_file.name}")

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.RECORD_VOICE,
    )

    await context.bot.send_audio(
        chat_id=update.effective_chat.id,
        audio=audio_file,
        title=audio_file.stem,
        thumbnail=audio_caption,
        disable_notification=True,
    )
    logger.info(f"audio sent {audio_file.name}")


async def send_sound(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_audio(update, context, get_random_audio())


async def send_civ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_audio(update, context, get_random_civilization())


async def send_taunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_audio(update, context, get_random_taunt())


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
