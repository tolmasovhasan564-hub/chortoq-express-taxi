import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import config
from database.db import init_db
from keyboards.menu import main_menu
from handlers.client import router as client_router
from handlers.driver import router as driver_router

# Konsolda xatoliklarni ko'rish
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

# Routerlarni ulash
dp.include_router(client_router)
dp.include_router(driver_router)

# /start buyrug'i
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom, {message.from_user.full_name}! 👋\n\n"
        f"Taksi botiga xush kelibsiz! Kerakli bo'limni tanlang:",
        reply_markup=main_menu
    )

async def main():
    await init_db()
    print("--- Ma'lumotlar bazasi yaratildi va bot ishga tushdi! ---")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())