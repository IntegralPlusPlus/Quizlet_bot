from config import bot_token
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from app.database.models import async_main
from app.handlers import router

async def main():
    #logging.basicConfig(level=logging.INFO)
    await async_main()
    
    bot = Bot(token = bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit') 