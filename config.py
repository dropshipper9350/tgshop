import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

NETWORK = os.getenv("NETWORK")

BINANCE_ADDRESS = os.getenv("BINANCE_ADDRESS")

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")