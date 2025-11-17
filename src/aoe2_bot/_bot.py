import logging
from os import environ
from pathlib import Path
from typing import Optional

from telegram.ext import ApplicationBuilder

from ._handlers import register_handlers
from .bootstrap import bootstrap

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

DEFAULT_ENV_FILE = "~/.config/aoe2-bot/env"


def get_token_from_env_file(env_file: str = DEFAULT_ENV_FILE) -> Optional[str]:
    """Read TGB_TOKEN from an environment file."""
    env_file_path = Path(env_file).expanduser()

    if not env_file_path.is_file():
        return None

    for line in env_file_path.read_text().splitlines():
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
        error = f"TGB_TOKEN not found. Set it as an environment variable or in {DEFAULT_ENV_FILE}"
        logger.error(error)
        raise EnvironmentError(error)

    return token


def main() -> None:
    bootstrap()
    application = ApplicationBuilder().token(get_token()).build()
    register_handlers(application)
    logger.info("Starting polling...")
    application.run_polling()
