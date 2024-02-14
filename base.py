import configparser
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command


def get_token():
    config = configparser.ConfigParser()
    config.read('secrets')
    telegram_section = config['telegram']
    token = telegram_section['token']
    return token


bot = Bot(token=get_token())
dp = Dispatcher()


async def said_hello(msg: types.Message):
    await msg.answer('Ola!')


# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.reply("Ola!")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Ola!")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    print('STAR BOT')
    asyncio.run(main())
    print('FINISH BOT')

