from typing import Any
import yaml
from pathlib import Path


config_dir = Path(__file__).parent.parent.resolve() / "config"
bot_dir = Path(__file__).parent.parent.resolve() / "bot"


# load yaml config
with open(config_dir / "config.yml", "r") as f:
    config_yaml = yaml.safe_load(f)


# config parameters
telegram_token = config_yaml["telegram_token"]
allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
admin_chat_id = config_yaml["admin_chat_id"]
admin_usernames = config_yaml["admin_usernames"]
mongodb_uri = f"mongodb://mongo:27017"
support_username = config_yaml["support_username"]
bot_username = config_yaml["bot_username"]
bot_name = config_yaml["bot_name"]
zadarma_api_key = config_yaml["zadarma_api_key"]
zadarma_api_secret = config_yaml["zadarma_api_secret"]
zadarma_number = config_yaml["zadarma_number"]
zadarma_sip = config_yaml["zadarma_sip"]
