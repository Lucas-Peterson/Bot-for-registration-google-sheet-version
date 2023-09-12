import asyncio
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import sqlite3


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

async def transfer_data():
    # Путь к JSON-файлу с ключами служебного аккаунта Google Cloud
    SERVICE_ACCOUNT_FILE = 'crypto-triode-391108-e1eb1490073a.json'

    # ID таблицы Google Sheets
    SPREADSHEET_ID = ''

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
        time.sleep(5)



if __name__ == '__main__':
    asyncio.run(schedule_transfer())