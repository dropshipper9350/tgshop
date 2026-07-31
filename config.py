import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS").split(",")]

NETWORK = os.getenv("NETWORK")

BINANCE_ADDRESS = os.getenv("BINANCE_ADDRESS")

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
