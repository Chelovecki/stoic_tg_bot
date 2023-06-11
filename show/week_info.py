import os

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text

# для получения информации о пользователе
from db.main_commands import get_user_data

# для отправки фото
from tools.send_photos import send_photo

# для получения информации о страницах
from tools.json import read_from_json

show_week_topic_router = Router()

@show_week_topic_router.message(Text('Теория недели'))
async def show_user_topic(message: Message):
    user_data = get_user_data(id_user=message.from_user.id)
    user_week = user_data['cur_week']
    all_photos = read_from_json(os.path.join(os.path.abspath('db'), 'week_path_images.json'))
    user_for_user = all_photos[f'week_{user_week}']
    await send_photo(message=message, photos_to_send=user_for_user)
