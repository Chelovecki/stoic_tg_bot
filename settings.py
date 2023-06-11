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

from tools.keyboards.default import main_menu_kb, settings_kb, show_for_some_reflections

settings_router = Router()

class SettingsAutomat(StatesGroup):
    null = State()

    waiting_answer = State()
    change_progress = State()
    chose_period_for_show = State()
@settings_router.message(Text('Настройки'))
async def settings(message: Message):
    await message.answer("""
    Что здесь находится:
- <b>файл</b> - получишь ссылку на файл
- <b>изменить прогресс</b> - изменишь текущую неделю и день
- <b>размышления</b> - показать размышления за какой-то период
- <b>изменить размышления</b> - если начал следующий день, а в прошлом что-то не дописал или забыл
    """, reply_markup=settings_kb(), parse_mode='html')

@settings_router.message(Text('Файл'))
async def send_link_file(message: Message):
    await message.answer('Уж прости, что я не сделал это по человечески отправкой файла. Лови ссылку:\nhttps://disk.yandex.ru/i/MXXxKc6bbjng1A')

@settings_router.message(Text('Изменить прогресс'))
async def change_progress(message: Message, state: FSMContext):
    await state.set_state(SettingsAutomat.change_progress)

    await message.answer(f'Окей, {message.from_user.first_name}, вводи новый прогресс в формате неделя *пробел* день. Пример:\n12 6\nгде 12 - неделя, а 6 - день')

@settings_router.message(SettingsAutomat.change_progress)
async def progress_handler(message: Message, state: FSMContext):
    try:
        week_number, day_number = message.text.split(' ')
        if (1 <= int(week_number) <= 52) and (1 <= int(day_number) <= 7):
            await state.set_state(SettingsAutomat.null)
            user_data = get_user_data(id_user=message.from_user.id)

            user_data['cur_week'] = week_number
            user_data['cur_day'] = day_number
            write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
            await message.answer('Я надеюсь, ты знаешь, что делаешь. Данные обновил. Проверить можешь, нажав "Размышления за сегодня"', reply_markup=main_menu_kb())
        else:
            await message.answer('Всего есть 52 недели по 7 дней в каждой.')
    except ValueError:
        await message.answer('Ты ввел что-то неправильно')


@settings_router.message(Text('Размышления'))
async def show_some_reflections(message: Message, state: FSMContext):
    await state.set_state(SettingsAutomat.chose_period_for_show)
    await message.answer("""
Отсюда ты можешь посмотреть размышления за разные периоды, а именно:
- <b>Вчера</b> - за весь вчерашний день 
- <b>Неделя</b> - вся эта неделя 
- <b>n неделя</b> - все размышления за ту неделю, номер которой ты введешь 
- <b>x неделя, y день</b> - размышления за определенный день определенной недели 
    """, reply_markup=show_for_some_reflections(), parse_mode='html')


@settings_router.message(SettingsAutomat.chose_period_for_show)
async def show_reflections(message: Message):
    if message.text == 'Вчера':
        await yesterday_reflections(message=message)
    elif message.text == 'Неделя':
        await week_reflections(message=message)

async def yesterday_reflections(message: Message):
    user_data = get_user_data(id_user=message.from_user.id)

    book_info = read_from_json(os.path.join(os.path.abspath(''), 'db', 'book_info.json'))

    now_week = int(user_data['cur_week'])
    now_day = int(user_data['cur_day'])
    if now_week == now_day == 1:
        await message.answer('Головой подумай как это может быть')
        return
    if now_day == 1 and now_week == 2:
        yesterday_day = 7
        yesterday_week = 1
    elif now_day == 1:
        yesterday_day = 7
        yesterday_week = now_week - 1
    else:
        yesterday_day = now_day - 1
        yesterday_week = now_week

    text_to_ouput = f'Неделя №{yesterday_week}, день №{yesterday_day}\n'
    text_to_ouput += f'Вопрос: <i>{book_info[f"week_{yesterday_week}"]["questions"][str(yesterday_day)]}</i>\n{60*"-"}\n'

    morning_reflections = user_data[str(yesterday_week)][str(yesterday_day)]["morning"]
    evening_reflections = user_data[str(yesterday_week)][str(yesterday_day)]["evening"]
    if morning_reflections:
        text_to_ouput += '<b>Утренние размышления</b>:\n'
        text_to_ouput += morning_reflections
        text_to_ouput += f'\n{60 * "-"}\n'
    if evening_reflections:
        text_to_ouput += '<b>Вечерние размышления</b>:\n'
        text_to_ouput += evening_reflections
    await message.answer(text=text_to_ouput, parse_mode='html', reply_markup=settings_kb())

async def week_reflections(message: Message):
    pass