import os

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

# для получения информации о пользователе
from db.main_commands import get_user_data

# для получения информации о страницах
from tools.json import read_from_json, write_in_json

# для создания автомата переходов
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from tools.keyboards.default import cancel_kb, main_menu_kb

add_reflections_router = Router()

class AddReflections(StatesGroup):
    morning = State()
    evening = State()
    null = State()




@add_reflections_router.message(Text('Добавить утренние размышления'))
async def morning_reflections(message: Message, state: FSMContext):
    await state.set_state(AddReflections.morning)
    user_data = get_user_data(id_user=message.from_user.id)
    path = os.path.join(os.path.abspath('db'), 'book_info.json')
    book_info = read_from_json(path)
    user_week, user_day = user_data['cur_week'], user_data['cur_day']
    question = f'День {((int(user_week) - 1) * 7) + int(user_day)}) '
    question += book_info[f'week_{user_week}']['questions'][str(user_day)]


    await message.answer(text=question, reply_markup=cancel_kb())

@add_reflections_router.message(AddReflections.morning)
async def morning(message: Message, state: FSMContext):

    await state.set_state(AddReflections.null)

    user_data = get_user_data(id_user=message.from_user.id)
    user_week, user_day = user_data['cur_week'], user_data['cur_day']
    user_day = str(user_day)
    user_week = str(user_week)

    if user_data[user_week][user_day]['morning'] is None:
        user_data[user_week][user_day]['morning'] = message.text
    else:
        user_data[user_week][user_day]['morning'] += f'\n{message.text}'
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Сохранил утренние размышления', reply_markup=main_menu_kb())



@add_reflections_router.message(Text('Добавить вечерние размышления'))
async def evening_reflections(message: Message, state: FSMContext):
    await state.set_state(AddReflections.evening)
    user_data = get_user_data(id_user=message.from_user.id)
    path = os.path.join(os.path.abspath('db'), 'book_info.json')
    book_info = read_from_json(path)
    user_week, user_day = user_data['cur_week'], user_data['cur_day']
    question = f'День {((int(user_week) - 1) * 7) + int(user_day)}) '
    question += book_info[f'week_{user_week}']['questions'][str(user_day)]


    await message.answer(text=question, reply_markup=cancel_kb())

@add_reflections_router.message(AddReflections.evening)
async def evening(message: Message, state: FSMContext):
    await state.set_state(AddReflections.null)

    user_data = get_user_data(id_user=message.from_user.id)
    user_week, user_day = user_data['cur_week'], user_data['cur_day']
    user_day = str(user_day)
    user_week = str(user_week)

    if user_data[user_week][user_day]['evening'] is None:
        user_data[user_week][user_day]['evening'] = message.text
    else:
        user_data[user_week][user_day]['evening'] += f'\n{message.text}'
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Сохранил вечерние мысли', reply_markup=main_menu_kb())




