from aiogram import Router, F
from aiogram.types import Message

from config import SUPPORT_USERNAME
from database.orders import get_orders_by_user

router = Router()


@router.message(F.text == "📦 My Orders")
async def orders(message: Message):

    rows = await get_orders_by_user(message.from_user.id)

    if not rows:
        await message.answer(
            "📦 You don't have any orders yet."
        )
        return

    text = "📦 <b>Your Orders</b>\n\n"

    for status, created, product_name in rows:
        text += f"🤖 {product_name} — {status}\n📅 {created}\n\n"

    await message.answer(
        text,
        parse_mode="HTML"
    )


@router.message(F.text == "🛟 Support")
async def support(message: Message):

    await message.answer(
        f"💬 Contact Admin\n\n{SUPPORT_USERNAME}"
    )