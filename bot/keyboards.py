from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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