from aiogram import types

from bot import dp, user_states
from modules import userbot, database


user_messages = {}

@dp.callback_query(lambda call: call.data == "start_send_message")
async def start_send_message(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = 'start_send_message_one_more'
    user_messages[user_id] = {}

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="📝 Выбрать из списка", callback_data="select_message_from_list")])
    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("✏️ *Введите текст сообщения:*",
                                    parse_mode="Markdown", reply_markup=markup)
    

@dp.callback_query(lambda call: call.data == "back_to_start_send_message")
async def back_to_start_send_message(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = 'start_send_message_one_more'

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="📝 Выбрать из списка", callback_data="select_message_from_list")])
    if user_messages.get(user_id):
        markup_buttons.append([types.InlineKeyboardButton(text="☑️ Продолжить", callback_data="continue_send_message")])
    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("✏️ *Введите следующее сообщение или нажмите 'Продолжить' для отправки сообщений.*",
                         parse_mode="Markdown", reply_markup=markup)
    

@dp.message(lambda message: user_states.get(message.from_user.id) == 'start_send_message_one_more')
async def start_send_message(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = 'start_send_message_one_more'

    if not user_messages.get(user_id):
        user_messages[user_id] = {}
    if not user_messages[user_id].get('text'):
        user_messages[user_id]['text'] = []

    user_messages[user_id]['text'].append(message.text)

    markup_buttons = []

    markup_buttons.append([types.InlineKeyboardButton(text="📝 Выбрать из списка", callback_data="select_message_from_list")])
    markup_buttons.append([types.InlineKeyboardButton(text="☑️ Продолжить", callback_data="continue_send_message")])
    markup_buttons.append([types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await message.answer("✏️ *Введите следующее сообщение или нажмите 'Продолжить' для отправки сообщений.*",
                         parse_mode="Markdown", reply_markup=markup)



@dp.callback_query(lambda call: call.data.startswith("start_send_message:"))
async def start_send_message(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = 'start_send_message_one_more'

    message_id = int(call.data.split(":")[-1])
    message = await database.get_saved_text(message_id)

    if not user_messages.get(user_id):
        user_messages[user_id] = {}
    if not user_messages[user_id].get('text'):
        user_messages[user_id]['text'] = []

    user_messages[user_id]['text'].append(message['text'])

    markup_buttons = []

    markup_buttons.append([types.InlineKeyboardButton(text="📝 Выбрать из списка", callback_data="select_message_from_list")])
    markup_buttons.append([types.InlineKeyboardButton(text="☑️ Продолжить", callback_data="continue_send_message")])
    markup_buttons.append([types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("✏️ *Введите следующее сообщение или нажмите 'Продолжить' для отправки сообщений.*",
                                    parse_mode="Markdown", reply_markup=markup)
    

@dp.callback_query(lambda call: call.data == "continue_send_message")
async def confirm_send_message(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = "minutes_and_count"

    if not user_messages.get(user_id, {}).get('text'):
        await call.answer("❌ Нет сообщений для отправки!", show_alert=True)
        return

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("📍 *Пожалуйста, укажите через запятую, с какой периодичностью (в минутах) и сколько раз вы хотели бы отправить сообщение.*\n\n"
                                    "📍 *Например: '60, 10' означает, что сообщение будет отправлено 10 раз с интервалом в один час*",
                                    parse_mode="Markdown", reply_markup=markup)
    

@dp.message(lambda message: user_states.get(message.from_user.id) == 'minutes_and_count')
async def send_message(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = None

    try:
        minutes, count = message.text.split(",")
        user_messages[user_id]['minutes'] = int(minutes)
        user_messages[user_id]['count'] = int(count)
    except:
        user_messages[user_id]['minutes'] = None
        user_messages[user_id]['count'] = None

        markup_buttons = []
        markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

        markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

        await message.answer("❌ *Неверный формат ввода!*\n\n"
                            "📍 *Пожалуйста, укажите через запятую, с какой периодичностью (в минутах) и сколько раз вы хотели бы отправить сообщение.*\n\n"
                            "📍 *Например: '60, 10' означает, что сообщение будет отправлено 10 раз с интервалом в один час*",
                            parse_mode="Markdown", reply_markup=markup)
        return

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="❌ Нет", callback_data="main_menu"),
                            types.InlineKeyboardButton(text="✅ Да", callback_data="confirm_send_message")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    user_messages_texts = "\n-------------------\n".join(user_messages[user_id]['text'])

    await message.answer(f"📍 Вы действительно хотите отправить данные сообщения {count} раз(а) с интервалом {minutes} минут(а)?\n\n"
                         f"{user_messages_texts}\n\n"
                         "📍 Нажмите кнопку ниже чтобы подтвердить.", reply_markup=markup)
    

@dp.callback_query(lambda call: call.data == "confirm_send_message")
async def confirm_send_message(call: types.CallbackQuery):
    user_id = call.from_user.id
    active_account = userbot.active_accounts[user_id]

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    if not active_account:
        await call.message.edit_text("❌ *Аккаунт не выбран!*", reply_markup=markup, parse_mode="Markdown")
        return
    
    selected_chats = userbot.selected_chats[active_account]

    if not selected_chats:
        await call.message.edit_text("❌ *Чаты не выбраны!*", reply_markup=markup, parse_mode="Markdown")
        return
    
    await call.message.edit_text("❗️ *Отправка сообщений запущена, это может занять некоторое время. Вы будете получать отчёты об каждом чате.*", reply_markup=markup, parse_mode="Markdown")
    
    for chat_id in selected_chats:
        chat_title = None
        success_count = 0
        error_count = 0

        chat_title, success_count, error_count = await userbot.send_delay_messages(active_account, chat_id, user_messages[user_id]['text'], user_messages[user_id]['minutes'], user_messages[user_id]['count'])

        if success_count == -999 and error_count == -999:
            await call.message.answer("❌ *Аккаунт невалиден! Остановка отправки сообщений.*", reply_markup=markup, parse_mode="Markdown")
            userbot.active_accounts[user_id] = None
            return
        
        await call.message.answer(f"❗️ Чат '{chat_title}' был обработан!\n\n"
                                    f"✅ Успешно отправлено: {success_count} сообщений\n"
                                    f"❌ Ошибок: {error_count}")
        
    await call.message.answer("✅ Все чаты были обработаны!", reply_markup=markup)