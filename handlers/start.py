from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from database.users import add_user
from keyboards.reply import home_keyboard
from config import CHANNEL_USERNAME
from keyboards.force_join import force_join_keyboard

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    # If a channel is configured, require the user to join it first
    if CHANNEL_USERNAME:
        try:
            member = await message.bot.get_chat_member(
                chat_id=CHANNEL_USERNAME,
                user_id=message.from_user.id
            )
            not_joined = member.status in ["left", "kicked"]
        except TelegramBadRequest:
            # Telegram throws this instead of "left" when it has no record
            # of the user ever being in the channel — treat it the same way
            not_joined = True

        if not_joined:
            await message.answer(
                "📢 Please join our channel first, then tap 'I've Joined'.",
                reply_markup=force_join_keyboard()
            )
            return

    await add_user(message.from_user)

    text = f"""
👋 Welcome {message.from_user.full_name}

🤖 Welcome to our ChatGPT Plus Store.

Choose an option below.
"""

    await message.answer(
        text,
        reply_markup=home_keyboard
    )

