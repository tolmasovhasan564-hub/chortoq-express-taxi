import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Logging sozlamasi
logging.basicConfig(level=logging.INFO)

# Token va Bot obyektlari
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Render kutadigan soxta HTTP server
async def handle(request):
    return web.Response(text="Bot is live 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# Asosiy ishga tushirish funksiyasi
async def main():
    # Veb-serverni orqa fonda ishga tushirish
    await start_web_server()
    
    # Handlers (buyruq va tugmalar) fayllarini ulash
    try:
        from handlers import start, client, admin
        # Agar handlers papkangizda boshqa fayllar bo'lsa, ularni ham shu yerda import qilasiz
    except ImportError:
        pass

    logging.info("Bot va Web Server muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())