import asyncio
from aiogram import Bot, Dispatcher
import logging

from aiogram.fsm.storage.memory import MemoryStorage

from utils import get_token
from parser import router as parser_router


bot = Bot(token=get_token())
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(parser_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
