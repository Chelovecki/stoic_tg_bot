import asyncio
import logging

from config_reader import config  # для получения токена бота

from aiogram import types
from aiogram.filters.command import Command
from aiogram.filters import Text
from aiogram import Bot, Dispatcher

import db.main_commands
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode='HTML')
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    this_user = message.from_user.id
    await message.answer('Привет, ты мне написал, а значит... ты мне написал. Давай короче к делу. Ты уже заполняешь эту книгу, или ты впервый раз?\nЕсли заполняешь, то введи  свой прогресс в форме')


# Запуск процесса поллинга новых апдейтов
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())