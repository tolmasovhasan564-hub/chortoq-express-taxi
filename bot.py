import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Tokenni tekshirish va ulash
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "BOTFATHER_TOKENINGIZNI_SHU_YERGA_YAZING"  # Agar env ishlamasa zaxira

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- HANDLERS (BUYRUQLAR) ---
# O'zingizning loyihangizdagi barcha handler fayllarni shu yerda chaqiring:
try:
    from handlers import start, client, admin
    # dp.include_router(...) yoki mos ravishda ulash:
except Exception as e:
    logging.error(f"Handlers importida xatolik: {e}")

# Render uchun soxta veb-server
async def handle(request):
    return web.Response(text="Bot running 24/7")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    logging.info("Bot ishga tushdi va xabarlarni kutmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())