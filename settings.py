import os

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

from typing import Union
# для получения информации о пользователе
from db.main_commands import get_user_data

# для получения информации о страницах
from tools.json import read_from_json, write_in_json

# для создания автомата переходов
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from tools.keyboards.default import main_menu_kb, settings_kb, show_for_some_reflections, \
    avaliable_change_reflections_period_kb

settings_router = Router()

class SettingsAutomat(StatesGroup):
    null = State()

    waiting_answer = State()
    change_progress = State()

    chose_period_for_show = State()

    wait_exact_week = State()
    wait_exact_day_and_week = State()

    wait_change_reflections = State()

class ChangeReflections(StatesGroup):
    today_morning = State()
    today_evening = State()

    yesterday_morning = State()
    yesterday_evening = State()

    some_morning = State()
    some_evening = State()

def get_yesterday_week_day(now_week: int, now_day: int) -> tuple[int] or bool:
    if now_week == now_day == 1:
        return False

    if now_day == 1 and now_week == 2:
        yesterday_day = 7
        yesterday_week = 1
    elif now_day == 1:
        yesterday_day = 7
        yesterday_week = now_week - 1
    else:
        yesterday_day = now_day - 1
        yesterday_week = now_week

    return yesterday_week, yesterday_day

@settings_router.message(Text('Прочее'))
async def settings(message: Message, state: FSMContext):
    await state.set_state(SettingsAutomat.null)
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


@settings_router.message(Text('Показать размышления'))
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
async def show_reflections(message: Message, state: FSMContext):
    if message.text == 'Вчера':
        await yesterday_reflections(message=message)
    elif message.text == 'Неделя':
        await week_reflections(message=message)
    elif message.text == 'n неделя':
        await state.set_state(SettingsAutomat.wait_exact_week)
        await message.answer('Введи номер недели от 1 до 52')
    elif message.text == 'x неделя, y день':
        await state.set_state(SettingsAutomat.wait_exact_day_and_week)
        await message.answer('Введи в формате неделя, день. Пример:\n<b>12, 6</b>, где 12 - неделя, а 6 - день')
    await state.set_state(SettingsAutomat.null)

async def yesterday_reflections(message: Message):
    user_data = get_user_data(id_user=message.from_user.id)

    book_info = read_from_json(os.path.join(os.path.abspath(''), 'db', 'book_info.json'))

    now_week = int(user_data['cur_week'])
    now_day = int(user_data['cur_day'])

    yesterday = get_yesterday_week_day(now_week=now_week, now_day=now_day)
    if not yesterday:
        await message.answer('Головой подумай как это может быть')
        return
    yesterday_week, yesterday_day = yesterday

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

async def week_reflections(message: Message, n_week:str=None):
    user_data = get_user_data(id_user=message.from_user.id)
    book_info = read_from_json(os.path.join(os.path.abspath(''), 'db', 'book_info.json'))
    if n_week:
        user_week = n_week
    else:
        user_week = str(user_data['cur_week'])

    texts_to_output = [f'Неделя №{user_week}']
    for day in range(1, int(user_data['cur_day']) + 1):
        text = f'День №{day}. Вопрос: <i>{book_info[f"week_{user_week}"]["questions"][str(day)]}</i>\n{60 * "-"}\n'

        morning_reflections = user_data[user_week][str(day)]["morning"]
        evening_reflections = user_data[user_week][str(day)]["evening"]

        if morning_reflections:
            text += '<b>Утренние размышления</b>:\n'
            text += morning_reflections
            text += f'\n{60 * "-"}\n'
        if evening_reflections:
            text += '<b>Вечерние размышления</b>:\n'
            text += evening_reflections
        # если утренние или вечерние записи были, добавляем в список для вывода потом
        if 'Утренние размышления' in text or 'Вечерние размышления' in text:
            texts_to_output.append(text)
    if len(texts_to_output) == 1:
        await message.answer('Но ты еще ничего не заполнял на этой неделе', reply_markup=settings_kb())
    else:
        for text in texts_to_output:
            # добавление маркапа ко всем сообщениям не делает работу программы быстрее, так что пофиг пусть так будет, чем только на последнее сообщение
            await message.answer(text, parse_mode='html', reply_markup=settings_kb())


@settings_router.message(SettingsAutomat.wait_exact_week)
async def get_week_number(message: Message):
    try:
        user_week = int(message.text)
        if 1 <= user_week <= 52:
            await week_reflections(message=message, n_week=str(user_week))
        else:
            await message.answer('Блять ну сказано же от 1 до 52.')
    except ValueError or TypeError:
        await message.answer('Ты что-то ввел не то')

@settings_router.message(SettingsAutomat.wait_exact_day_and_week)
async def get_week_day_reflection(message: Message):
    try:
        week, day = message.text.split(', ')
        if (1 <= int(week) <= 52) and (1 <= int(day) <= 7):
            user_data = get_user_data(id_user=message.from_user.id)
            book_info = read_from_json(os.path.join(os.path.abspath(''), 'db', 'book_info.json'))

            text = f'Неделя №{week}, день №{day}.\nВопрос: <i>{book_info[f"week_{week}"]["questions"][day]}</i>\n{60 * "-"}\n'

            morning_reflections = user_data[week][day]["morning"]
            evening_reflections = user_data[week][day]["evening"]

            if morning_reflections:
                text += '<b>Утренние размышления</b>:\n'
                text += morning_reflections
                text += f'\n{60 * "-"}\n'
            if evening_reflections:
                text += '<b>Вечерние размышления</b>:\n'
                text += evening_reflections
            if 'Утренние размышления' in text or 'Вечерние размышления' in text:
                await message.answer(text=text, parse_mode='html', reply_markup=settings_kb())
            else:
                await message.answer('Ничего не заполненно')

        else:
            await message.answer('Неделей всего 52, дней в неделе сколько?')

    except ValueError or TypeError:
        await message.answer('Не понимаю')

@settings_router.message(Text('Изменить размышления'))
async def change_reflections(message: Message, state: FSMContext):
    await state.set_state(SettingsAutomat.wait_change_reflections)
    await message.answer('Можешь изменить за сегодня, за вчера, и за какой-то день недели', reply_markup=avaliable_change_reflections_period_kb())

@settings_router.message(SettingsAutomat.wait_change_reflections)
async def change_reflections_handler(message: Message, state: FSMContext):
    user_data = get_user_data(id_user=message.from_user.id)
    now_week = str(user_data['cur_week'])
    now_day = str(user_data['cur_day'])

    await message.answer(
        'Вот все то, что ты писал за этот день. Скопируй себе, отредактируй что надо (ну или полностью перепиши), а потом отправь мне этот текст, а я его сохраню')
    if message.text == 'Сегодня утро':
        await state.set_state(ChangeReflections.today_morning)
        await send_reflections_to_change(message=message, state=state, user_data=user_data, morning=True, week=now_week, day=now_day)

    elif message.text == 'Сегодня вечер':
        await state.set_state(ChangeReflections.today_evening)
        await send_reflections_to_change(message=message, state=state, user_data=user_data, evening=True, week=now_week, day=now_day)

    elif message.text in ('Вчера утро', 'Вчера вечер'):
        now_day = int(now_day)
        now_week = int(now_week)

        yesterday = get_yesterday_week_day(now_week=now_week, now_day=now_day)

        if not yesterday:
            await message.answer('Какое тебе вчера? Ты только первый день заполняешь дневник')
            return

        yesterday_week, yesterday_day = map(str, yesterday)

        if message.text == 'Вчера утро':
            await state.set_state(ChangeReflections.yesterday_morning)
            await send_reflections_to_change(message=message, state=state, user_data=user_data, morning=True, week=yesterday_week,day=yesterday_day)
        else:
            await state.set_state(ChangeReflections.yesterday_evening)
            await send_reflections_to_change(message=message, state=state, user_data=user_data, evening=True,
                                             week=yesterday_week, day=yesterday_day)

async def send_reflections_to_change(message: Message, user_data:dict, state: FSMContext, morning:bool=False, evening:bool=False, week:str=None, day:str=None):
    book_info = read_from_json(os.path.join(os.path.abspath(''), 'db', 'book_info.json'))

    text = f'Неделя №{week}, день №{day}\nВопрос: <i>{book_info[f"week_{week}"]["questions"][day]}</i>\n{60*"-"}\n'
    morning_info = user_data[week][day]["morning"]
    evening_info = user_data[week][day]["evening"]

    # если ничего чел не писал, то пишем ему и брейкаем функцию
    if morning_info is None and morning:
        await message.answer('А ты писал что-то утром, чтобы это можно было изменять?')
        return
    if evening_info is None and evening:
        await message.answer('А ты писал что-то вечером, чтобы это можно было изменять?')
        return

    if morning:
        text += f'<b>Утренние размышления:</b>\n'
        await message.answer(f'{text}<code>{morning_info}</code>', parse_mode='html')

    if evening:
        text += f'<b>Вечерние размышления:</b>\n'
        await message.answer(f'{text}<code>{evening_info}</code>', parse_mode='html')


@settings_router.message(ChangeReflections.today_morning)
async def today_morning_handler(message: Message):

    user_data = get_user_data(id_user=message.from_user.id)

    week = str(user_data['cur_week'])
    day = str(user_data['cur_day'])

    user_data[week][day]["morning"] = message.text
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Сохранил изменения в сегодняшнем утре', reply_markup=settings_kb())


@settings_router.message(ChangeReflections.today_evening)
async def today_evening_handler(message: Message):
    user_data = get_user_data(id_user=message.from_user.id)

    week = str(user_data['cur_week'])
    day = str(user_data['cur_day'])

    user_data[week][day]["evening"] = message.text
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Сохранил изменения в сегодняшнем вечере', reply_markup=settings_kb())


@settings_router.message(ChangeReflections.yesterday_morning)
async def yesterday_morning_handler(message: Message):

    user_data = get_user_data(id_user=message.from_user.id)

    week = str(user_data['cur_week'])
    day = str(user_data['cur_day'])

    yesterday = get_yesterday_week_day(now_week=int(week), now_day=int(day))
    yesterday_week, yesterday_day = map(str, yesterday)

    user_data[yesterday_week][yesterday_day]["morning"] = message.text
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Сохранил изменения в вчерашнем утре', reply_markup=settings_kb())

@settings_router.message(ChangeReflections.yesterday_evening)
async def yesterday_evening_handler(message: Message):
    user_data = get_user_data(id_user=message.from_user.id)

    week = user_data['cur_week']
    day = user_data['cur_day']

    yesterday = get_yesterday_week_day(now_week=week, now_day=day)

    yesterday_week, yesterday_day = map(str, yesterday)

    user_data[yesterday_week][yesterday_day]["evening"] = message.text
    write_in_json(name_and_path=user_data['file_path'], dictionary=user_data)
    await message.answer('Сохранил изменения в вчерашнем вечере', reply_markup=settings_kb())





