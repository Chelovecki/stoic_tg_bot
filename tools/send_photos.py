import logging


from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.types import Message, BufferedInputFile

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def send_photo(message: Message, photos_to_send: list):
    media_group = []
    for path in photos_to_send:
        image = BufferedInputFile.from_file(path=path)
        media_group.append(InputMediaPhoto(media=image))

    await message.answer_media_group(media=media_group)