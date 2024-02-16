import configparser
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram import F

import resume_parser

from RabotaUa import RobotaUaParser

def get_token():
    config = configparser.ConfigParser()
    config.read('secrets')
    telegram_section = config['telegram']
    token = telegram_section['token']
    return token


bot = Bot(token=get_token())
dp = Dispatcher()
router = Router()
logging.basicConfig(level=logging.INFO)


def register_message_handlers():
    dp.message.register(say_hello, Command('hello'))
    dp.message.register(start_searching, Command('start'))
    dp.message.register(robota_ua, (F.text == 'robota.ua'))
    dp.message.register(work_ua, (F.text == 'work.ua'))


async def say_hello(message: types.Message):
    await message.answer('Ola amigo!')


async def start_searching(message: types.Message):
    kb = [
        [types.KeyboardButton(text='robota.ua')],
        [types.KeyboardButton(text='work.ua')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Choose the source"
    )
    await message.answer('What site do you want to use for searching?', reply_markup=keyboard)


async def robota_ua(message: types.Message):
    await message.reply('robota.ua')

    parser = resume_parser.source_choice('1')
    parser.parse()

    print(candidates)


async def work_ua(message: types.Message):
    await message.reply('work.ua')


async def select_category(message: types.Message):
    parser.set_category({message})

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    register_message_handlers()
    asyncio.run(main())


