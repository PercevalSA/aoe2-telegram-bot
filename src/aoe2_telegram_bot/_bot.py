import logging
from os import environ
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder

from ._folders import env_file
from ._handlers import register_handlers
from .bootstrap import bootstrap

logger = logging.getLogger(__name__)


def get_token_from_env_file() -> Optional[str]:
    """Read TGB_TOKEN from an environment file."""
    if not env_file.is_file():
        return None

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("TGB_TOKEN="):
            return line.split("=", 1)[1].strip()

    return None


def get_token() -> str:
    # Check environment variable first (highest precedence)
    token = environ.get("TGB_TOKEN")

    # Fall back to config file
    if token is None:
        token = get_token_from_env_file()

    if token is None:
        error = (
            f"TGB_TOKEN not found. Set it as an environment variable or in {env_file}"
        )
        logger.error(error)
        raise EnvironmentError(error)

    return token


def main() -> None:
    """Entry point for aoe2-telegram-bot command."""
    # Configure logging only if not already configured
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )

    bootstrap()
    application = ApplicationBuilder().token(get_token()).build()
    register_handlers(application)
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.MESSAGE)
