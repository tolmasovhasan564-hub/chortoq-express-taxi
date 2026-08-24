import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- HANDLERS (BUYRUQLARNI ULASH QISMI) ---
# Papkangizdagi barcha handler fayllarini shu yerga import qiling:
from handlers import start  # Agar boshqa fayllar bo'lsa (masalan: client, admin), vergul bilan qo'shing

# Routerlarni Dispatcher'ga ulash:
dp.include_router(start.router)
# Agar boshqa routerlar bo'lsa, ularni ham qo'shing:
# dp.include_router(client.router)
# dp.include_router(admin.router)


# --- RENDER VEB-SERVER QISMI ---
async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    # Veb-serverni orqa fonda ishga tushirish
    await start_web_server()
    logging.info("Bot tayyor va xabarlarni kutmoqda!")
    
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())