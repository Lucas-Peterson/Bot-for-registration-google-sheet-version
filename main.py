from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.config import TOKEN
from bot.handlers import register_handlers
from database.db import init_db

# Инициализация бота и диспетчера
API_TOKEN = TOKEN

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def main():
    # Инициализация базы данных
    init_db()

    # Регистрация обработчиков
    register_handlers(dp)

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()
