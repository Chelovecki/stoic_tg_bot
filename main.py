import asyncio
import logging
# для получения токена бота
import os

from config_reader import config

# для удобной работы бота
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters import Text
from aiogram import Bot, Dispatcher

# импортруем роутеры
from show.week_info import show_week_topic_router
from set.add_morning_evening_info import add_reflections_router
from show.show_my_day_reflections import show_day_reflections_router

# db
from db.main_commands import add_user_in_db, get_user_data

# json
from tools.json import read_from_json, write_in_json

# клавиатуры
from tools.keyboards.default import process_new_user, main_menu_kb, sure_or_not

# для создания автомата переходов
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode='HTML')

# Диспетчер
dp = Dispatcher()
dp.include_routers(show_week_topic_router, add_reflections_router, show_day_reflections_router)

# автомат переходов
class Filling_User_Info(StatesGroup):
    await_week_day_info = State()

    am_i_sure_nex_day = State()

    null = State()

# Хэндлер на команду /start
@dp.message(Command('start'))
async def cmd_start(message: Message):
    add_user_in_db(id_user=message.from_user.id)
    await message.answer('Привет, ты мне написал, а значит... ты мне написал. Давай короче к делу. Ты уже заполняешь эту книгу, или ты впервый раз?', reply_markup=process_new_user())


@dp.message(Text('Отмена'))
@dp.message(Command('menu'))
@dp.message(Text('Главное меню'))
async def main_menu(message: Message):
    await message.answer(text='Что сделаем?', reply_markup=main_menu_kb())


@dp.message(Text('Я уже заполняю дневник'))
async def im_yet(message: Message, state: FSMContext):
    await state.set_state(Filling_User_Info.await_week_day_info)
    await message.answer(text='Введи свой прогресс в формате номер_недели:какой_по_счету_день_недели')

@dp.message(Text('Я еще не смешарик'))
async def im_not_yet(message: Message):
    user_data = get_user_data(id_user=message.from_user.id)
    if user_data['cur_week'] and user_data['cur_day']:
        await message.answer('ты не можешь сбросить свои данные крч мне бля впадлу щас все пилить все эти да нет деревья')
        return
    user_data['cur_week'] = 1
    user_data['cur_day'] = 1
    user_data['file_path'] = os.path.join(os.path.abspath('db'), 'users_data', f'{message.from_user.id}.json')
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Ок, тогда начнем с начала', reply_markup=main_menu_kb())

@dp.message(Filling_User_Info.await_week_day_info)
async def get_cur_week_and_day(message: Message, state: FSMContext):
    try:
        week, day = message.text.split(':')
        if not(1 <= int(week) <= 52):
            raise Exception
        if not(1 <= int(day) <= 7):
            raise Exception

        user_data = get_user_data(id_user=message.from_user.id)
        user_data['cur_week'] = week
        user_data['cur_day'] = day
        user_data['file_path'] = os.path.join(os.path.abspath('db'), 'users_data', f'{message.from_user.id}.json')
        write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
        await message.answer('Ок', reply_markup=main_menu_kb())
        
    except Exception:
        await message.answer('Что-то ты не то ввел')
        await im_yet(message=message, state=state)




@dp.message(Text('Следующий день'))
async def confirm(message: Message, state: FSMContext):
    await state.set_state(Filling_User_Info.am_i_sure_nex_day)
    await message.answer('Уверен? Если что, можешь потом исправить/дописать.', reply_markup=sure_or_not())


@dp.message(Filling_User_Info.am_i_sure_nex_day)
async def confirm_if_yes(message: Message, state: FSMContext):
    await state.set_state(Filling_User_Info.null)
    if message.text == 'Да, уверен':
        user_data = get_user_data(id_user=message.from_user.id)

        user_day = int(user_data['cur_day'])
        user_week = int(user_data['cur_week'])

        user_day += 1
        if user_day == 8:
            user_week += 1
            user_day = 1

        user_data['cur_week'] = user_week
        user_data['cur_day'] = user_day
        write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
        await message.answer(f'Ок, неделя №{user_week}, вопрос №{user_day}', reply_markup=main_menu_kb())
    else:
        await state.set_state(Filling_User_Info.null)
        await message.answer('Оболтус, хватит на кнопочки тыкать', reply_markup=main_menu_kb())

# Запуск процесса поллинга новых апдейтов
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())