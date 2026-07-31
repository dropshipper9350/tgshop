from aiogram.utils.keyboard import InlineKeyboardBuilder


def quantity_keyboard(product_id):
    builder = InlineKeyboardBuilder()

    for qty in [20, 30]:
        builder.button(
            text=str(qty),
            callback_data=f"qty:{product_id}:{qty}"
        )

    builder.button(
        text="✏️ Custom Amount",
        callback_data=f"qty:{product_id}:custom"
    )

    builder.adjust(5, 1)

    return builder.as_markup()


def products_list_keyboard(products):
    """Shown to buyers - one button per active product."""
    builder = InlineKeyboardBuilder()

    for product in products:
        product_id, name, price = product[0], product[1], product[2]
        builder.button(
            text=f"{name} — ${price}",
            callback_data=f"buyproduct:{product_id}"
        )

    builder.adjust(1)

    return builder.as_markup()


def stock_product_keyboard(products):
    """Shown to admin when choosing which product to upload accounts for."""
    builder = InlineKeyboardBuilder()

    for product in products:
        product_id, name = product[0], product[1]
        builder.button(
            text=name,
            callback_data=f"stockfor:{product_id}"
        )

    builder.adjust(1)

    return builder.as_markup()


def admin_products_list_keyboard(products):
    """Shown to admin - one button per product, opens management screen."""
    builder = InlineKeyboardBuilder()

    for product in products:
        product_id, name, active = product[0], product[1], product[4]
        status_icon = "✅" if active else "🚫"
        builder.button(
            text=f"{status_icon} {name}",
            callback_data=f"manageproduct:{product_id}"
        )

    builder.button(
        text="➕ Add Product",
        callback_data="addproduct"
    )

    builder.adjust(1)

    return builder.as_markup()


def product_manage_keyboard(product_id, active):
    """Activate/Deactivate + Delete buttons for a single product."""
    builder = InlineKeyboardBuilder()

    if active:
        builder.button(
            text="🚫 Deactivate",
            callback_data=f"deactivate:{product_id}"
        )
    else:
        builder.button(
            text="✅ Activate",
            callback_data=f"activate:{product_id}"
        )

    builder.button(
        text="🗑 Delete",
        callback_data=f"deleteproduct:{product_id}"
    )

    builder.button(
        text="⬅️ Back to Products",
        callback_data="backtoproducts"
    )

    builder.adjust(2, 1)

    return builder.as_markup()


def buy_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📷 Show Binance QR",
        callback_data="show_qr"
    )

    builder.button(
        text="📋 Copy Wallet",
        callback_data="wallet"
    )

    builder.button(
        text="✅ I Have Paid",
        callback_data="paid"
    )

    builder.adjust(1)

    return builder.as_markup()


def admin_keyboard(user_id, payment_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Approve",
        callback_data=f"approve:{payment_id}:{user_id}"
    )

    builder.button(
        text="❌ Reject",
        callback_data=f"reject:{payment_id}:{user_id}"
    )

    builder.adjust(2)

    return builder.as_markup()
