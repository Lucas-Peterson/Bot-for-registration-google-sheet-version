from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    question1 = State()  # Состояние для получения имени пользователя
    question2 = State()  # Состояние для получения названия компании
    question3 = State()  # Состояние для получения контакта пользователя
    question4 = State()  # Состояние для получения email пользователя
