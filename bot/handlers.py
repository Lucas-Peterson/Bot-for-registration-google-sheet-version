from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from bot.keyboards import create_main_menu_keyboard, create_return_keyboard, create_return_keyboard2, create_smi_keyboard, create_preza_keyboard
from bot.states import RegistrationStates
from database.db import add_registration_data, transfer_data_to_google_sheets

def register_handlers(dp):
    @dp.message_handler(Command('start'))
    async def start_command(message: types.Message):
        await message.reply('Хэй!')
        await RegistrationStates.question1.set()

    @dp.message_handler(state=RegistrationStates.question1)
    async def process_question1(message: types.Message, state: FSMContext):
        answer = message.text
        add_registration_data(user_id=message.from_user.id, name=answer)
        await RegistrationStates.next()
        await message.reply("Приятно познакомиться! В какой компании вы работаете?")

    @dp.message_handler(state=RegistrationStates.question2, content_types=types.ContentType.TEXT)
    async def process_question2(message: types.Message, state: FSMContext):
        answer = message.text
        add_registration_data(user_id=message.from_user.id, company=answer)
        await RegistrationStates.next()

        request_contact_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        request_contact_keyboard.add(types.KeyboardButton(text="Отправить контакт", request_contact=True))
        await message.reply(
            "Принято, поделитесь со мной контактом, чтобы мы могли с вами в дальнейшем связываться? В обмен на телефон и электронную почту я отблагодарю вас материалами по нашим кейсам.",
            reply_markup=request_contact_keyboard
        )

    @dp.message_handler(state=RegistrationStates.question3, content_types=types.ContentType.CONTACT)
    async def process_question3(message: types.Message, state: FSMContext):
        contact = message.contact
        phone_number = contact.phone_number
        add_registration_data(user_id=message.from_user.id, contact=phone_number)

        remove_keyboard = types.ReplyKeyboardRemove()
        await RegistrationStates.next()
        await message.reply("Спасибо! Пожалуйста, введите email", reply_markup=remove_keyboard)

    @dp.message_handler(state=RegistrationStates.question4)
    async def process_question4(message: types.Message, state: FSMContext):
        email = message.text
        if '@' not in email:
            await message.reply("Пожалуйста, введите корректный адрес электронной почты.")
            return

        add_registration_data(user_id=message.from_user.id, email=email)
        await state.finish()

        # Передача данных в Google Sheets после завершения регистрации
        transfer_data_to_google_sheets()

        await message.reply("Все готово. О каком кейсе интересно узнать в первую очередь?", reply_markup=create_main_menu_keyboard())

    @dp.callback_query_handler()
    async def handle_callback_query(callback_query: types.CallbackQuery):
        if callback_query.data == "read_cases":
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                        text="Расскажу про то, как мы реализовывали обучение:", reply_markup=create_smi_keyboard())
        elif callback_query.data == "get_presentation":
            with open('PDF.pdf', 'rb') as presentation_file:
                await bot.send_document(chat_id=callback_query.message.chat.id, document=presentation_file, reply_markup=create_return_keyboard2())
        elif callback_query.data == "return":
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                        text='О чём хотите узнать?', reply_markup=create_main_menu_keyboard())
        elif callback_query.data == "return2":
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id-1)
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=callback_query.message.chat.id, text= 'О чём хотите узнать?', reply_markup=create_main_menu_keyboard())
, reply_markup=create_preza_keyboard())
