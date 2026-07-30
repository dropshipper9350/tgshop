from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CHANNEL_USERNAME


def force_join_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📢 Join Channel",
        url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
    )

    kb.button(
        text="✅ I've Joined",
        callback_data="check_join"
    )

    kb.adjust(1)

    return kb.as_markup()