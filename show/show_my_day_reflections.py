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

from tools.keyboards.default import main_menu_kb

show_day_reflections_router = Router()
class ShowSpecialNotes(StatesGroup):
    wait_input_week_day = State()

    null = State()


@show_day_reflections_router.message(Text('Покажи размышления за сегодня'))
async def show_today_reflections(message: Message):
    text_for_ouput = ''
    user_data = get_user_data(id_user=message.from_user.id)
    path = os.path.join(os.path.abspath('db'), 'book_info.json')
    book_info = read_from_json(path)

    user_week, user_day = user_data['cur_week'], user_data['cur_day']
    user_day = str(user_day)
    user_week = str(user_week)
    text_for_ouput += f'Неделя №{user_week}, День №{user_day}\n'
    text_for_ouput += f'Вопрос: <i>{book_info[f"week_{user_week}"]["questions"][user_day]}\n{"-"*14}</i>\n'

    morning = user_data[user_week][user_day]['morning']
    evening = user_data[user_week][user_day]['evening']

    if morning:
        text_for_ouput += f'<b>Утренние размышления:</b>\n'
        text_for_ouput += morning
        text_for_ouput += f'\n{"-"*14}\n'
    if evening:
        text_for_ouput += f'\n<b>Вечерние размышления:</b>\n'
        text_for_ouput += evening
        text_for_ouput += '\n'

    await message.answer(text_for_ouput, parse_mode='HTML')


@show_day_reflections_router.message(Text('Покажи размышления за...'))
async def chose_day_for_chose(message: Message, state: FSMContext):
    await state.set_state(ShowSpecialNotes.wait_input_week_day)
    await message.answer(text='Напиши номер недели и день в формате <b>неделя:день</b>', parse_mode='HTML')


@show_day_reflections_router.message(ShowSpecialNotes.wait_input_week_day)
async def show_info(message:Message, state: FSMContext):


    try:
        week, day = message.text.split(':')
        if not(1 <= int(week) <= 52):
            raise Exception
        if not(1 <= int(day) <= 7):
            raise Exception
        await state.set_state(ShowSpecialNotes.null)

        user_data = get_user_data(id_user=message.from_user.id)

        morning = user_data[week][day]['morning']
        evening = user_data[week][day]['evening']

        text_to_output = ''

        if morning:
            text_to_output += '<b>Утренние размышления:</b>\n'
            text_to_output += f'{morning}\n{"-"*10}\n'
        if evening:
            text_to_output += '<b>Вечерние размышления:</b>\n'
            text_to_output += evening

        if not text_to_output:
            await message.answer('Ничего нет')
        else:
            await message.answer(text=text_to_output, reply_markup=main_menu_kb(), parse_mode='HTML')

    except ValueError:
        await message.answer('Что-то ты не то ввел')

