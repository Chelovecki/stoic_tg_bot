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

show_day_reflections_router = Router()

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
    text_for_ouput += f'Вопрос: <i>{book_info[f"week_{user_week}"]["questions"][user_day]}\n{"-"*14}</i>'

    morning = user_data[user_week][user_day]['morning']
    evening = user_data[user_week][user_day]['evening']

    if morning:
        text_for_ouput += f'<b>Утренние размышления:</b>\n'
        text_for_ouput += morning
    if evening:
        text_for_ouput += f'\n<b>Вечерние размышления:</b>\n'
        text_for_ouput += evening
        text_for_ouput += '\n'
    await message.answer(text_for_ouput, parse_mode='HTML')

