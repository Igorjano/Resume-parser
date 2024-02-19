from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.main import Parser

router = Router()


@router.message(Command('search'))
async def cmd_search(message: types.Message, state: FSMContext):
    await state.set_state(Parser.site)
    kb = [
        [types.KeyboardButton(text='robota.ua'),
         types.KeyboardButton(text='work.ua')],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="What site?"
    )
    await message.answer('Let\'s select the source',
                         reply_markup=keyboard)
