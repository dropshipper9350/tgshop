import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

from database.models import create_tables

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.buy import router as buy_router
from handlers.payment import router as payment_router
from handlers.admin import router as admin_router
from handlers.delivery import router as delivery_router
from handlers.force_join import router as force_join_router


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()


# Register Routers
dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(buy_router)
dp.include_router(payment_router)
dp.include_router(admin_router)
dp.include_router(delivery_router)
dp.include_router(force_join_router)


async def main():

    # Create database tables
    await create_tables()

    print("=" * 40)
    print("✅ Database Ready")
    print("🤖 Telegram Digital Store Started")
    print("=" * 40)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())