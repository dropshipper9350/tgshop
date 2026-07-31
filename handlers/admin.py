from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.reply import admin_keyboard
from keyboards.inline import (
    stock_product_keyboard,
    admin_products_list_keyboard,
    product_manage_keyboard
)

from states.admin import AdminState
from states.broadcast import BroadcastState

from database.stock import account_exists, add_account, get_stock_count, get_total_stock_count
from database.orders import get_last_orders, get_total_orders, get_total_revenue
from database.users import get_total_users, get_all_users
from database.payments import get_pending_payments
from database.products import (
    add_product,
    get_all_products,
    get_product,
    set_product_active,
    delete_product
)

from config import ADMIN_IDS

router = Router()


@router.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        "🛠 <b>Admin Panel</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard
    )


# ---------------- Product Management ----------------

@router.message(F.text == "🗂 Manage Products")
async def manage_products(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    products = await get_all_products(active_only=False)

    if not products:
        await message.answer(
            "🗂 <b>No products yet.</b>\n\nTap below to add your first one.",
            parse_mode="HTML",
            reply_markup=admin_products_list_keyboard([])
        )
        return

    await message.answer(
        "🗂 <b>Your Products</b>\n\n✅ = active, 🚫 = hidden from buyers\nTap one to manage it.",
        parse_mode="HTML",
        reply_markup=admin_products_list_keyboard(products)
    )


@router.callback_query(F.data == "backtoproducts")
async def back_to_products(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    products = await get_all_products(active_only=False)

    await callback.message.edit_text(
        "🗂 <b>Your Products</b>\n\n✅ = active, 🚫 = hidden from buyers\nTap one to manage it.",
        parse_mode="HTML",
        reply_markup=admin_products_list_keyboard(products)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("manageproduct:"))
async def manage_single_product(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    product_id = int(callback.data.split(":")[1])
    product = await get_product(product_id)

    if product is None:
        await callback.answer("Product not found.", show_alert=True)
        return

    stock = await get_stock_count(product_id)
    status = "✅ Active" if product[4] else "🚫 Hidden"

    text = f"""
🤖 <b>{product[1]}</b>

💰 Price: ${product[2]}
📝 {product[3]}

📦 Stock: {stock}
Status: {status}
"""

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=product_manage_keyboard(product_id, bool(product[4]))
    )

    await callback.answer()


@router.callback_query(F.data.startswith("activate:"))
async def activate_product(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    product_id = int(callback.data.split(":")[1])
    await set_product_active(product_id, True)
    await callback.answer("✅ Product activated.")
    await manage_single_product(callback)


@router.callback_query(F.data.startswith("deactivate:"))
async def deactivate_product(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    product_id = int(callback.data.split(":")[1])
    await set_product_active(product_id, False)
    await callback.answer("🚫 Product hidden from buyers.")
    await manage_single_product(callback)


@router.callback_query(F.data.startswith("deleteproduct:"))
async def delete_product_handler(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    product_id = int(callback.data.split(":")[1])
    deleted = await delete_product(product_id)

    if not deleted:
        await callback.answer(
            "❌ Can't delete — this product already has accounts under it. "
            "Deactivate it instead.",
            show_alert=True
        )
        return

    await callback.answer("🗑 Product deleted.")

    products = await get_all_products(active_only=False)
    await callback.message.edit_text(
        "🗂 <b>Your Products</b>\n\n✅ = active, 🚫 = hidden from buyers\nTap one to manage it.",
        parse_mode="HTML",
        reply_markup=admin_products_list_keyboard(products)
    )


@router.callback_query(F.data == "addproduct")
async def add_product_start(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    await callback.message.edit_text(
        "➕ <b>Add Product</b>\n\nWhat's the product name?",
        parse_mode="HTML"
    )

    await state.set_state(AdminState.waiting_for_product_name)
    await callback.answer()


@router.message(AdminState.waiting_for_product_name)
async def add_product_name(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    name = message.text.strip()

    if not name:
        await message.answer("❌ Please send a valid product name.")
        return

    await state.update_data(name=name)
    await message.answer("💰 What's the price in USD? (e.g. 1.5)")
    await state.set_state(AdminState.waiting_for_product_price)


@router.message(AdminState.waiting_for_product_price)
async def add_product_price(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Please send a valid positive number, e.g. 1.5")
        return

    await state.update_data(price=price)
    await message.answer("📝 Write a short description for this product:")
    await state.set_state(AdminState.waiting_for_product_description)


@router.message(AdminState.waiting_for_product_description)
async def add_product_description(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    description = message.text.strip()

    if not description:
        await message.answer("❌ Please send a description.")
        return

    data = await state.get_data()

    product_id = await add_product(data["name"], data["price"], description)

    await message.answer(
        f"""
✅ <b>Product Added!</b>

🤖 {data['name']}
💰 ${data['price']}
📝 {description}

Now add stock for it via <b>📤 Upload Accounts</b>.
""",
        parse_mode="HTML"
    )

    await state.clear()


# ---------------- Stock ----------------

@router.message(F.text == "📦 Stock")
async def stock(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    products = await get_all_products(active_only=False)

    if not products:
        await message.answer("📦 No products yet. Add one first via 🗂 Manage Products.")
        return

    text = "📦 <b>Current Stock</b>\n\n"

    for product in products:
        count = await get_stock_count(product[0])
        text += f"🤖 {product[1]}: {count} available\n"

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📤 Upload Accounts")
async def upload_accounts(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    products = await get_all_products(active_only=False)

    if not products:
        await message.answer(
            "❌ You need to add a product first — use 🗂 Manage Products."
        )
        return

    await message.answer(
        "📤 Which product are these accounts for?",
        reply_markup=stock_product_keyboard(products)
    )


@router.callback_query(F.data.startswith("stockfor:"))
async def choose_stock_product(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Not authorized.", show_alert=True)
        return

    product_id = int(callback.data.split(":")[1])
    product = await get_product(product_id)

    await state.update_data(stock_product_id=product_id)

    await callback.message.edit_text(
        f"""
📤 <b>Upload accounts for {product[1]}</b>

Send <b>one account per line</b> using this format:

<code>email:password:2FA_SECRET</code>

<b>Example:</b>
<code>
account1@gmail.com:Password123:JBSWY3DPEHPK3PXP
</code>

⚠️ Make sure every line contains exactly:
• Email
• Password
• 2FA Secret
""",
        parse_mode="HTML"
    )

    await state.set_state(AdminState.waiting_for_accounts)
    await callback.answer()


@router.message(AdminState.waiting_for_accounts)
async def save_accounts(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()
    product_id = data.get("stock_product_id")

    if product_id is None:
        await message.answer("❌ Something went wrong — please start again from 📤 Upload Accounts.")
        await state.clear()
        return

    lines = message.text.splitlines()

    added = 0
    duplicates = 0

    for line in lines:

        parts = line.split(":")

        if len(parts) != 3:
            continue

        email = parts[0].strip()
        password = parts[1].strip()
        twofa_secret = parts[2].strip()

        if not email or not password or not twofa_secret:
            continue

        if await account_exists(email):
            duplicates += 1
            continue

        await add_account(
            product_id,
            email,
            password,
            twofa_secret
        )

        added += 1

    await message.answer(
        f"""
✅ Upload Complete

📥 Added: {added}

⚠️ Duplicates Skipped: {duplicates}
"""
    )

    await state.clear()


# ---------------- Payments / Orders / Users / Stats ----------------

@router.message(F.text == "💳 Pending Payments")
async def pending(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    payments = await get_pending_payments()

    if not payments:

        await message.answer(
            "✅ No pending payments."
        )
        return

    text = "💳 <b>Pending Payments</b>\n\n"

    for payment in payments:

        payment_id = payment[0]
        user_id = payment[1]
        quantity = payment[3]

        text += (
            f"🆔 Payment #{payment_id}\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"🔢 Quantity: {quantity}\n\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@router.message(F.text == "📋 Orders")
async def orders(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    rows = await get_last_orders()

    if not rows:
        await message.answer(
            "📋 No orders yet."
        )
        return

    text = "📋 <b>Recent Orders</b>\n\n"

    for user_id, product_name, created in rows:

        text += (
            f"👤 User: <code>{user_id}</code>\n"
            f"🤖 Product: {product_name}\n"
            f"📅 {created}\n\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@router.message(F.text == "👥 Users")
async def users(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    total = await get_total_users()

    users = await get_all_users()

    text = f"👥 <b>Total Users:</b> {total}\n\n"

    if users:

        text += "<b>Latest Users</b>\n\n"

        for user in users[:10]:

            text += (
                f"👤 {user[1]}\n"
                f"<code>{user[0]}</code>\n\n"
            )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@router.message(F.text == "📊 Statistics")
async def statistics(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    users = await get_total_users()
    orders = await get_total_orders()
    revenue = await get_total_revenue()
    stock = await get_total_stock_count()
    pending = len(await get_pending_payments())

    await message.answer(
        f"""
📊 <b>Store Statistics</b>

👥 Users: {users}

📦 Orders: {orders}

📚 Stock: {stock}

💳 Pending Payments: {pending}

💰 Revenue: ${revenue}
""",
        parse_mode="HTML"
    )


@router.message(F.text == "📢 Broadcast")
async def broadcast(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        "📢 Send the message you want to broadcast."
    )

    await state.set_state(
        BroadcastState.waiting_message
    )


@router.message(BroadcastState.waiting_message)
async def send_broadcast(message: Message, state: FSMContext):

    if message.from_user.id not in ADMIN_IDS:
        return

    users = await get_all_users()

    sent = 0
    failed = 0

    for user in users:

        try:

            await message.bot.send_message(
                user[0],
                message.text
            )

            sent += 1

        except Exception:

            failed += 1

    await message.answer(
        f"""
✅ Broadcast Completed

📨 Sent : {sent}

❌ Failed : {failed}
"""
    )

    await state.clear()
