import logging
import os
import platform
from pathlib import Path
from zipfile import ZipFile

import requests

from ._folders import (
    audio_archives,
    audio_folder,
    audio_url,
    bootstrap_file,
    service_file,
)

logger = logging.getLogger(__name__)


def download_bin(url: str, dest_folder: Path) -> Path:
    logger.info(f"Downloading {url} to {dest_folder}")
    local_filename = dest_folder / url.split("/")[-1]
    # NOTE the stream=True parameter below to avoid storing the entire file into memory at once
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)

    logger.info(f"Download {local_filename.name} complete")
    return local_filename


def unzip(zip_file: Path, dest_folder: Path, *, remove_zip: bool = False) -> None:
    logger.info(f"Unzipping {zip_file} to {dest_folder}")
    with ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(dest_folder)
    if remove_zip:
        logger.info(f"Removing {zip_file}")
        zip_file.unlink()


def install_audio() -> None:
    logger.info("Installing audio files...")
    for archive in audio_archives:
        archive_url = audio_url + archive
        zip_file = download_bin(archive_url, audio_folder)
        unzip(zip_file, audio_folder, remove_zip=True)


def create_audio_folder() -> None:
    logger.info("Creating audio folder if missing")
    audio_folder.mkdir(exist_ok=True)


def check_bootstrap() -> bool:
    return bootstrap_file.exists()


def finish_bootstrap() -> None:
    bootstrap_file.touch()
    logger.info("audio files bootstrap complete")


def bootstrap() -> None:
    create_audio_folder()
    if check_bootstrap():
        logger.info("Audio files already installed")
        return

    install_audio()
    finish_bootstrap()


def create_systemd_service_file() -> None:
    if platform.system() != "Linux":
        logger.error("Systemd service is only available on Linux")
        return

    logger.info("Creating systemd service file...")

    user = os.environ.get("USER")
    service_content = service_file.read_text()
    service_content = service_content.replace("User=%i", f"User={user}")
    service_content = service_content.replace("Group=%i", f"Group={user}")
    service_content = service_content.replace("%h", f"/home/{user}")

    dest_file = Path.cwd() / "aoe2-telegram-bot.service"
    dest_file.write_text(service_content)
    logger.info(f"Service file installed in current folder {dest_file}")

    logger.info(
        "install systemd file with sudo cp aoe2-telegram-bot.service /etc/systemd/system/aoe2-telegram-bot.service"
    )
    logger.info(
        "Then run: sudo systemctl daemon-reload && sudo systemctl enable aoe2-telegram-bot && sudo systemctl start aoe2-telegram-bot"
    )
