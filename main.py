import logging
import sqlite3


import asyncio
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import *



from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


API_TOKEN = TOKEN


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS registration (
        user_id INTEGER PRIMARY KEY,
        name TEXT ,
        company TEXT,
        contact TEXT,
        email TEXT
        )
''')
conn.commit()


class RegistrationStates(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()


@dp.message_handler(Command('start'))
async def start_command(message: types.Message):
    await message.reply('Здравствуйте! Здорово, что вы заинтересовались проектами INEX service design, я совсем молодой бот, но уже кое-что умею, например, делиться нашими кейсами в обмен на ваши контакты.\nДавайте знакомиться!\n<a href="https://inex.partners/)">INEX service design</a> — международное агентство по разработке решений для роста и повышения эффективности бизнеса в каждой точке контакта с клиентом.\n Мы занимаемся консалтингом, обучением и популяризацией сервис-дизайна. \nКак обращаться к вам? Введите Имя и Фамилию или ФИО', parse_mode="HTML")

    # Устанавливаем начальное состояние
    await RegistrationStates.question1.set()


@dp.message_handler(state=RegistrationStates.question1)
async def process_question1(message: types.Message, state: FSMContext):
    # Сохраняем ответ на первый вопрос
    answer = message.text

    # Сохраняем ответ в базу данных
    cursor.execute("INSERT INTO registration (user_id, name) VALUES (?, ?)", (message.from_user.id, answer))
    conn.commit()

    # Переходим ко второму вопросу
    await RegistrationStates.next()
    await message.reply("Приятно познакомиться! В какой компании вы работаете?")


@dp.message_handler(state=RegistrationStates.question2, content_types=types.ContentType.TEXT)
async def process_question2(message: types.Message, state: FSMContext):
    # Сохраняем ответ на второй вопрос
    answer = message.text

    # Сохраняем ответ в базу данных
    cursor.execute("UPDATE registration SET company = ? WHERE user_id = ?", (answer, message.from_user.id))
    conn.commit()

    # Переходим к третьему вопросу
    await RegistrationStates.next()

    # Создаем клавиатуру для запроса контакта
    request_contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    request_contact_keyboard.add(KeyboardButton(text="Отправить контакт", request_contact=True))

    await message.reply(
        "Принято, поделитесь со мной контактом, чтобы мы могли с вами в дальнейшем связываться? В обмен на телефон и электронную почту я отблагодарю вас материалами по нашим кейсам.",
        reply_markup=request_contact_keyboard
    )


@dp.message_handler(state=RegistrationStates.question3, content_types=types.ContentType.CONTACT)
async def process_question3(message: types.Message, state: FSMContext):
    # Сохраняем контакт из сообщения
    contact = message.contact
    phone_number = contact.phone_number

    # Сохраняем ответ в базу данных
    cursor.execute("UPDATE registration SET contact = ? WHERE user_id = ?", (phone_number, message.from_user.id))
    conn.commit()

    remove_keyboard = ReplyKeyboardRemove()

    # Переходим к четвертому вопросу
    await RegistrationStates.next()
    await message.reply("Спасибо! Пожалуйста, введите email", reply_markup=remove_keyboard)

@dp.message_handler(state=RegistrationStates.question4)
async def process_question4(message: types.Message, state: FSMContext):
    # Сохраняем ответ на четвертый вопрос
    answer = message.text

    # Проверяем наличие символа "@" в ответе
    if '@' not in answer:
        await message.reply("Пожалуйста, введите корректный адрес электронной почты.")
        return

    # Сохраняем ответ в базу данных
    cursor.execute("UPDATE registration SET email = ? WHERE user_id = ?", (answer, message.from_user.id))
    conn.commit()

    # Завершаем регистрацию
    await state.finish()
    await message.reply("Все готово. О каком кейсе интересно узнать в первую очередь?", reply_markup=create_main_menu_keyboard())


def create_return_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data="return")
    )
    return keyboard


def create_return_keyboard2():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data="return2")
    )
    return keyboard


def create_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Прочитать в СМИ про наши кейсы", callback_data="read_cases"),
        InlineKeyboardButton(text="Получить презентацию по микрообучению", callback_data="get_presentation")
    )
    return keyboard

def create_smi_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Перекрёсток", callback_data="pr"),
        InlineKeyboardButton(text="Агентство стратегических инициатив (АСИ)", callback_data="asi"),
        InlineKeyboardButton(text="Назад", callback_data="return")
    )
    return keyboard

def create_preza_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data="read_cases")
    )
    return keyboard

@dp.callback_query_handler()
async def handle_callback_query(callback_query: types.CallbackQuery):
    if callback_query.data == "read_cases":
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text="Расскажу про то, как мы реализовывали обучение:", reply_markup= create_smi_keyboard())
    if callback_query.data == "get_presentation":
        # Отправка файла
        with open('CC_INEX_Baranova.pdf', 'rb') as presentation_file:
            await bot.send_document(chat_id=callback_query.message.chat.id, document=presentation_file, reply_markup=create_return_keyboard2())

    if callback_query.data == "return":
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text='О чём хотите узнать?', reply_markup=create_main_menu_keyboard())
    if callback_query.data == "return2":
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id-1)
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id)
        await bot.send_message(chat_id=callback_query.message.chat.id, text= 'О чём хотите узнать?', reply_markup=create_main_menu_keyboard())
    if callback_query.data == "pr":
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text='И слава Боту: как в «Перекрёстке» провели марафон улучшения сервиса для клиентов: <a href="https://inex.partners/)">«Кейс «Перекрестка»</a>: как торговая сеть запустила «Сервис-марафоны» и повысила показатель NPS.', parse_mode="HTML", reply_markup=create_preza_keyboard())
    if callback_query.data == "asi":
        await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                    text='<a href="https://inex.partners/)">Трудности материнства</a> (и при чем здесь сервис-дизайн)?  ',parse_mode="HTML", reply_markup=create_preza_keyboard())

'''
async def transfer_data():
    # Путь к JSON-файлу с ключами служебного аккаунта Google Cloud
    SERVICE_ACCOUNT_FILE = 'crypto-triode-391108-e1eb1490073a.json'

    # ID таблицы Google Sheets
    SPREADSHEET_ID = '1mNoitEXwRSngHXI2gdrShCXOYWBV86-NNC4qcuxp_0Y'

    # Создание экземпляра служебного аккаунта Google Cloud
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])

    # Создание экземпляра клиента Google Sheets API
    service = build('sheets', 'v4', credentials=credentials)

    # Выбор рабочего листа
    sheet = service.spreadsheets()

    # Выполнение SQL-запроса для получения данных из таблицы "registration"
    cursor.execute('SELECT * FROM registration')
    data = cursor.fetchall()

    # Преобразование данных в формат, понятный для Google Sheets API (список списков)
    values = [[str(item) for item in row] for row in data]

    # Запись данных в Google Sheets
    range_name = 'Sheet1'  # Название листа, в который вы хотите записать данные
    body = {'values': values}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption='RAW', body=body).execute()

    print("Данные успешно отправлены в базу данных")


async def schedule_transfer():
    while True:
        await transfer_data()
'''

if __name__ == '__main__':
    '''
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_transfer())
    '''
    executor.start_polling(dp, skip_updates=True)

