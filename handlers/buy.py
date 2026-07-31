from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import NETWORK
from database.products import get_all_products, get_product
from keyboards.inline import quantity_keyboard, buy_keyboard, products_list_keyboard
from states.payment import PaymentState

router = Router()

MAX_QUANTITY = 999
MIN_QUANTITY = 20


@router.message(F.text == "🛒 Buy")
async def buy(message: Message):

    products = await get_all_products(active_only=True)

    if not products:
        await message.answer(
            "😔 No products are available right now. Please check back later."
        )
        return

    await message.answer(
        "🛍 Choose a product:",
        reply_markup=products_list_keyboard(products)
    )


@router.callback_query(F.data.startswith("buyproduct:"))
async def choose_product(callback: CallbackQuery, state: FSMContext):

    product_id = int(callback.data.split(":")[1])

    product = await get_product(product_id)

    if product is None or product[4] == 0:
        await callback.answer("This product is no longer available.", show_alert=True)
        return

    await state.update_data(product_id=product_id)

    await callback.message.edit_text(
        f"🔢 How many <b>{product[1]}</b> would you like to buy?",
        parse_mode="HTML",
        reply_markup=quantity_keyboard(product_id)
    )

    await callback.answer()


async def show_order_summary(product_id, quantity, state: FSMContext, send):
    """
    Saves the chosen quantity and shows the product summary with total price.
    'send' is a function that actually sends/edits the message
    (kept separate so both the button flow and the typed flow can reuse it).
    """

    product = await get_product(product_id)

    if product is None or product[4] == 0:
        await send("❌ This product is no longer available.")
        return

    name = product[1]
    price = product[2]
    description = product[3]

    await state.update_data(product_id=product_id, quantity=quantity)
    await state.set_state(None)

    total = round(price * quantity, 2)

    text = f"""
🤖 <b>{name}</b>

━━━━━━━━━━━━━━━━━━

🔢 Quantity
{quantity}

💰 Total Price
${total}

📝 Description
{description}

━━━━━━━━━━━━━━━━━━

💳 Payment Method
Binance

🌐 Network
{NETWORK}

━━━━━━━━━━━━━━━━━━
"""

    await send(text, parse_mode="HTML", reply_markup=buy_keyboard())


@router.callback_query(F.data.startswith("qty:") & F.data.contains(":custom"))
async def ask_custom_quantity(callback: CallbackQuery, state: FSMContext):

    product_id = int(callback.data.split(":")[1])

    await state.update_data(product_id=product_id)

    await callback.message.edit_text(
        f"✏️ Type how many you want ({MIN_QUANTITY}-{MAX_QUANTITY}):"
    )

    await state.set_state(PaymentState.waiting_for_custom_quantity)

    await callback.answer()


@router.message(PaymentState.waiting_for_custom_quantity)
async def receive_custom_quantity(message: Message, state: FSMContext):

    text = message.text.strip() if message.text else ""

    if not text.isdigit():
        await message.answer(
            f"❌ Please send a whole number, like {MIN_QUANTITY}. Try again (1-{MAX_QUANTITY}):"
        )
        return

    quantity = int(text)

    if quantity < MIN_QUANTITY or quantity > MAX_QUANTITY:
        await message.answer(
            f"❌ Please enter a number between {MIN_QUANTITY} and {MAX_QUANTITY}."
        )
        return

    data = await state.get_data()
    product_id = data.get("product_id")

    await show_order_summary(product_id, quantity, state, message.answer)


@router.callback_query(F.data.startswith("qty:"))
async def set_quantity(callback: CallbackQuery, state: FSMContext):

    _, product_id, qty = callback.data.split(":")
    product_id = int(product_id)
    quantity = int(qty)

    await show_order_summary(product_id, quantity, state, callback.message.edit_text)

    await callback.answer()
