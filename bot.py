import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher

# Render port talab qilgani uchun soxta veb-server
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# Asosiy ishga tushirish qismi
async def main():
    await start_web_server()
    # Bot va Dispatcher obyektlaringizni shu yerda chaqiring
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())