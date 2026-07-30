from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from config import (
    BINANCE_ADDRESS,
    ADMIN_ID
)

from database.products import get_product

from states.payment import PaymentState
from keyboards.inline import admin_keyboard
from database.payments import create_payment, is_payment_pending

from database.stock import claim_account

from database.orders import create_order

from database.payments import (
    approve_payment,
    reject_payment,
    get_payment
)

router = Router()


@router.callback_query(F.data == "show_qr")
async def show_qr(callback: CallbackQuery):

    photo = FSInputFile("qr/binance_qr.jpg")

    await callback.message.answer_photo(
        photo,
        caption="📱 Scan this Binance QR and complete your payment."
    )

    await callback.answer()


@router.callback_query(F.data == "wallet")
async def wallet(callback: CallbackQuery):

    await callback.message.answer(
        f"""
📋 Binance Wallet

<code>{BINANCE_ADDRESS}</code>

(Long press to copy)
""",
        parse_mode="HTML"
    )

    await callback.answer()


@router.callback_query(F.data == "paid")
async def paid(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        "📷 Please send your payment screenshot."
    )

    await state.set_state(
        PaymentState.waiting_for_screenshot
    )

    await callback.answer()


@router.message(
    PaymentState.waiting_for_screenshot,
    F.photo
)
async def receive_screenshot(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()
    quantity = data.get("quantity", 1)
    product_id = data.get("product_id")

    product = await get_product(product_id)
    product_name = product[1] if product else "Unknown"
    total_price = round(product[2] * quantity, 2) if product else 0

    photo = message.photo[-1].file_id
    payment_id = await create_payment(
        message.from_user.id,
        product_id,
        photo,
        quantity
    )

    caption = f"""
🔔 <b>New Payment Request</b>

👤 User:
{message.from_user.full_name}

🆔 ID:
<code>{message.from_user.id}</code>

🤖 Product:
{product_name}

🔢 Quantity:
{quantity}

💰 Price:
${total_price}
"""

    await message.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=admin_keyboard(
        message.from_user.id,
        payment_id
        )
    )

    await message.answer(
        "✅ Screenshot received.\n\nPlease wait for admin verification."
    )

    await state.clear()

@router.callback_query(F.data.startswith("approve:"))
async def approve(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Not authorized.", show_alert=True)
        return

    _, payment_id, user_id = callback.data.split(":")

    payment_id = int(payment_id)
    user_id = int(user_id)

    payment = await get_payment(payment_id)
    from database.payments import is_payment_pending

    if not await is_payment_pending(payment_id):
        await callback.answer(
        "This payment has already been processed.",
        show_alert=True
        )
        return

    if payment is None:

        await callback.answer(
            "Payment not found.",
            show_alert=True
        )
        return

    payment_product_id = payment[1]
    quantity = payment[2]

    product = await get_product(payment_product_id)
    product_name = product[1] if product else "Unknown Product"

    accounts = []

    for _ in range(quantity):
        account = await claim_account(payment_product_id)
        if account is None:
            break
        accounts.append(account)

    if not accounts:

        await callback.message.answer(
            f"❌ No {product_name} accounts in stock."
        )
        return

    await approve_payment(payment_id)

    accounts_text = ""

    for account in accounts:

        account_id = account[0]
        email = account[1]
        password = account[2]
        twofa_secret = account[3]

        await create_order(
            user_id,
            payment_product_id,
            account_id
        )

        accounts_text += f"""
📧 Email
<code>{email}</code>

🔑 Password
<code>{password}</code>

🔐 2FA Secret
<code>{twofa_secret}</code>

━━━━━━━━━━━━━━━━━━
"""

    shortage_note = ""
    if len(accounts) < quantity:
        shortage_note = f"\n⚠️ Only {len(accounts)} of {quantity} requested accounts were in stock. Contact support for the rest.\n"

    await callback.bot.send_message(
        chat_id=user_id,
        text=f"""
🎉 <b>Payment Approved!</b>

🤖 {product_name} x{len(accounts)}
{shortage_note}
{accounts_text}
Thank you ❤️
""",
        parse_mode="HTML"
    )

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ APPROVED",
        parse_mode="HTML",
        reply_markup=None
    )

    await callback.answer("Approved")

@router.callback_query(F.data.startswith("reject:"))
async def reject(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Not authorized.", show_alert=True)
        return

    _, payment_id, user_id = callback.data.split(":")

    payment_id = int(payment_id)

    await reject_payment(payment_id)

    await callback.bot.send_message(
        chat_id=int(user_id),
        text="""
❌ Your payment was rejected.

Please contact support.
"""
    )

    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ REJECTED",
        parse_mode="HTML",
        reply_markup=None
    )

    await callback.answer("Rejected")