from pathlib import Path

current_module_folder = Path(__file__).parent
images_folder = current_module_folder / "images"
audio_caption = images_folder / "aok-ico.png"
audio_folder = current_module_folder / "audio"
bootstrap_file = audio_folder / "installation_complete"

audio_url = (
    "https://media.githubusercontent.com/media/PercevalSA/aoe2-telegram-bot/main/audio/"
)
audio_archives = [
    "civilization.zip",
    "sound.zip",
    "taunt.zip",
]

service_file = current_module_folder / "distro" / "aoe2-telegram-bot.service"

config_folder = Path.home() / ".config/aoe2-telegram-bot"
env_file = config_folder / "env"
files_id_db = config_folder / "files_id_db.json"
