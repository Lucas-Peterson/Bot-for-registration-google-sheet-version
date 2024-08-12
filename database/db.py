import sqlite3
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.config import GOOGLE_SERVICE_ACCOUNT_FILE, SPREADSHEET_ID


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            company TEXT,
            contact TEXT,
            email TEXT
        )
    ''')
    conn.commit()

# Функция для добавления данных в базу данных
def add_registration_data(user_id, name=None, company=None, contact=None, email=None):
    if name:
        cursor.execute("INSERT INTO registration (user_id, name) VALUES (?, ?)", (user_id, name))
    if company:
        cursor.execute("UPDATE registration SET company = ? WHERE user_id = ?", (company, user_id))
    if contact:
        cursor.execute("UPDATE registration SET contact = ? WHERE user_id = ?", (contact, user_id))
    if email:
        cursor.execute("UPDATE registration SET email = ? WHERE user_id = ?", (email, user_id))
    conn.commit()

# Функция для передачи данных в Google Sheets
def transfer_data_to_google_sheets():
    credentials = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    cursor.execute('SELECT * FROM registration')
    data = cursor.fetchall()
    values = [[str(item) for item in row] for row in data]

    range_name = 'Sheet1'
    body = {'values': values}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption='RAW', body=body).execute()

    print("Данные успешно отправлены в Google Sheets")
