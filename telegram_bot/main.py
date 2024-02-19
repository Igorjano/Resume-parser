import asyncio
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from utils import get_token
from utils import load_data, sorting
from parsers.RobotaUa import RobotaUaParser
from parsers.WorkUa import WorkUaParser

from routers.commands.base import router as main_router
from routers.commands.user_commands import router as user_commands_router

bot = Bot(token=get_token())
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(main_router, user_commands_router)

cities = ['Київ', 'Дніпро', 'Харків', 'Запоріжжя', 'Львів', 'Одеса', 'search by all cities']
experience = ['up to 1 year', '1', '2', '5', '10', 'without experience', 'don\'t use this parameter']
salary_lst = ['20000', '30000', '40000', '50000', '70000', '100000', 'don\'t specify the salary']


class Parser(StatesGroup):
    site = State()
    category = State()
    search_text = State()
    location = State()
    experience = State()
    min_salary = State()
    max_salary = State()
    photo = State()
    parse = State()


@dp.message(Command('cancel'))
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(
        "Cancelled",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Parser.site, F.text.in_(['robota.ua', 'work.ua']))
async def select_site(message: types.Message, state: FSMContext):
    await message.answer("Let's see what we got here ")
    await state.update_data(site=message.text.lower())
    await state.set_state(Parser.category)
    kb = [
        [types.KeyboardButton(text='Job position'),
         types.KeyboardButton(text='Skills or keywords')],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Category'
    )
    await message.answer('Choose category', reply_markup=keyboard)
#
# @dp.message(Parser.site)
# async def incorrect_site(message: types.Message):
#     await


@dp.message(Parser.category, F.text.lower().in_(['job position', 'skills or keywords']))
async def select_category(message: types.Message, state: FSMContext):
    await state.update_data(category='1' if message.text.lower() == 'job position' else '2')
    await state.set_state(Parser.search_text)
    await message.answer('What are we looking for?', reply_markup=ReplyKeyboardRemove())


@dp.message(Parser.category)
async def incorrect_category(message: types.Message):
    await message.answer(f'There are no such category {message.text}. Please choose from categories below')


@dp.message(Parser.search_text)
async def search_text(message: types.Message, state: FSMContext):
    await state.update_data(search_text=message.text)
    await state.set_state(Parser.location)
    builder = ReplyKeyboardBuilder()
    for city in cities:
        builder.add(types.KeyboardButton(text=city))
    builder.adjust(3)
    await message.reply('Great!')
    await message.answer('Choose city from below or enter the name of the city',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(Parser.location)
async def select_location(message: types.Message, state: FSMContext):
    if message.text == 'search by all cities':
        await state.update_data(location=None)
    else:
        await state.update_data(location=message.text)
    await state.set_state(Parser.experience)
    builder = ReplyKeyboardBuilder()
    for year in experience:
        builder.add(types.KeyboardButton(text=year))
    builder.adjust(3)
    await message.answer('Choose experience or type your value',
                         reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Years of experience'))


@dp.message(Parser.experience)
async def select_experience(message: types.Message, state: FSMContext):
    if message.text == 'up to 1 year':
        await state.update_data(experience=0.5)
    elif message.text == 'without experience':
        await state.update_data(experience=0)
    elif message.text == 'don\'t use this parameter':
        await state.update_data(experience=None)
    else:
        try:
            await state.update_data(experience=int(message.text))
        except ValueError:
            await state.update_data(experience=None)
            await message.reply('You enter invalid value. Experience wasn\'t set')
    await state.set_state(Parser.min_salary)
    builder = ReplyKeyboardBuilder()
    for salary in salary_lst:
        builder.add(types.KeyboardButton(text=salary))
    builder.adjust(3)
    await message.answer('Choose or type minimum salary',
                         reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Salary minimum'))


@dp.message(Parser.min_salary)
async def select_min_salary(message: types.Message, state: FSMContext):
    if message.text == 'don\t specify the salary':
        await state.update_data(min_salary=None)
    else:
        try:
            await state.update_data(min_salary=int(message.text))
        except ValueError:
            await state.update_data(min_salary=None)
            await message.reply('Salary must be an integer! Minimum salary wasn\'t set')
    await state.set_state(Parser.max_salary)
    builder = ReplyKeyboardBuilder()
    for salary in salary_lst:
        builder.add(types.KeyboardButton(text=salary))
    builder.adjust(3)
    await message.answer('What about maximum salary?',
                         reply_markup=builder.as_markup(resize_keyboard=True,
                                                        input_field_placeholder='Salary maximum'))


@dp.message(Parser.max_salary)
async def select_max_salary(message: types.Message, state: FSMContext):
    if message.text == 'don\t specify the salary':
        await state.update_data(max_salary=None)
    else:
        try:
            await state.update_data(max_salary=int(message.text))
        except ValueError:
            await state.update_data(max_salary=None)
            await message.reply('Salary must be an integer! Maximum salary wasn\'t set')
    await state.set_state(Parser.photo)
    kb = [
        [types.KeyboardButton(text='yes'),
         types.KeyboardButton(text='no')],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="yes or no?"
    )
    await message.answer('Do you want resume only with photo?',
                         reply_markup=keyboard)


@dp.message(Parser.photo)
async def select_photo(message: types.Message, state: FSMContext):
    if message.text == 'yes':
        await state.update_data(photo='yes')
    else:
        await state.update_data(photo=None)
    await state.set_state(Parser.parse)
    kb = [
        [types.KeyboardButton(text='search')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        # input_field_placeholder=""
    )
    await message.answer('Awesome! All parameters are set so I can start searching',
                         reply_markup=keyboard)


@dp.message(Parser.parse, F.text == 'search')
async def parse(message: types.Message, state: FSMContext):
    options = await state.get_data()
    print(options)
    await message.answer('Wait some time so I prepare the result', reply_markup=ReplyKeyboardRemove())
    if options['site'] == 'robota.ua':
        p = RobotaUaParser(options['category'], options['search_text'], options['location'],
                           options['experience'], options['min_salary'], options['max_salary'],
                           options['photo'])
    elif options['site'] == 'work.ua':
        p = WorkUaParser(options['category'], options['search_text'], options['location'],
                           options['experience'], options['min_salary'], options['max_salary'],
                           options['photo'])
    # print(p)
    p.parse()
    candidates = load_data()
    result = sorting(candidates)
    for res in result[:5]:
        await message.answer(res['cv_page'], prefer_small_media=True)








async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
