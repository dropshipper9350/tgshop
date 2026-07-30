import os
import aiosqlite

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE = os.path.join(DATA_DIR, "shop.db")


async def get_db():
    return await aiosqlite.connect(DATABASE)