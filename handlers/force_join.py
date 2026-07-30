from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from config import CHANNEL_USERNAME
from database.users import add_user
from keyboards.reply import home_keyboard

router = Router()


@router.callback_query(F.data == "check_join")
async def check_join(callback: CallbackQuery):

    try:
        member = await callback.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=callback.from_user.id
        )
        not_joined = member.status in ["left", "kicked"]
    except TelegramBadRequest:
        not_joined = True

    if not_joined:

        await callback.answer(
            "❌ Please join the channel first.",
            show_alert=True
        )
        return

    await add_user(callback.from_user)

    await callback.message.edit_text(
        "✅ Channel verification successful!"
    )

    await callback.message.answer(
        "Welcome to the store.",
        reply_markup=home_keyboard
    )

    await callback.answer()