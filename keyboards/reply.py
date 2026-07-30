from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


home_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛒 Buy")
        ],
        [
            KeyboardButton(text="📦 My Orders"),
            KeyboardButton(text="🛟 Support")
        ]
    ],
    resize_keyboard=True
)


admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🗂 Manage Products"),
            KeyboardButton(text="📤 Upload Accounts")
        ],
        [
            KeyboardButton(text="📦 Stock"),
            KeyboardButton(text="💳 Pending Payments")
        ],
        [
            KeyboardButton(text="📋 Orders"),
            KeyboardButton(text="👥 Users")
        ],
        [
            KeyboardButton(text="📊 Statistics"),
            KeyboardButton(text="📢 Broadcast")
        ]
    ],
    resize_keyboard=True
)
