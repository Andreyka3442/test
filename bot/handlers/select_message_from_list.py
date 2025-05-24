from aiogram import types

from bot import dp, user_states
from modules import database
from handlers.start_send_message import user_messages


@dp.callback_query(lambda call: call.data.startswith("select_message_from_list"))
async def select_message_from_list(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = None

    markup_buttons = []
    texts = await database.get_saved_texts()

    page_size = 7
    pages_count = (len(texts) - 1) // page_size
    try:
        page = int(call.data.split(":")[-1])
    except:
        page = 0

    if page < 0:
        page = pages_count
    elif page > pages_count:
        page = 0

    start = page * page_size
    end = start + page_size

    markup_buttons.append([types.InlineKeyboardButton(text="➕ Добавить сообщение", callback_data="add_saved_text")])

    for index, text_message in enumerate(texts[start:end]):
        emoji_status = "✅" if text_message['text'] in user_messages[user_id].get('text', []) else "❌"
        markup_buttons.append([types.InlineKeyboardButton(text=f"{emoji_status} {index + 1}.", callback_data="pass"),
                                types.InlineKeyboardButton(text=f"{text_message['text']}", callback_data=f"select_text_from_list:{text_message['id']}:{page}"),
                                 types.InlineKeyboardButton(text="🗑", callback_data=f"delete_saved_text:{text_message['id']}")])
        
    markup_buttons.append([types.InlineKeyboardButton(text=f"◀️", callback_data=f"select_message_from_list:{page - 1}"),
                            types.InlineKeyboardButton(text=f"{page+1}/{pages_count+1}", callback_data="pass"),
                                types.InlineKeyboardButton(text=f"▶️", callback_data=f"select_message_from_list:{page + 1}")])

    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_start_send_message")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("🔽 *Выберите сообщение:*",
                                    parse_mode="Markdown", reply_markup=markup)
    

@dp.callback_query(lambda call: call.data.startswith("select_text_from_list:"))
async def select_text_from_list(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = None

    page = int(call.data.split(":")[-1])
    text_message_id = int(call.data.split(":")[-2])

    message = await database.get_saved_text(text_message_id)

    if not user_messages.get(user_id):
        user_messages[user_id] = {}
    if not user_messages[user_id].get('text'):
        user_messages[user_id]['text'] = []

    if message['text'] in user_messages[user_id].get('text', []):
        user_messages[user_id]['text'].remove(message['text'])
    else:
        user_messages[user_id]['text'].append(message['text'])

    markup_buttons = []
    texts = await database.get_saved_texts()

    page_size = 7
    pages_count = (len(texts) - 1) // page_size

    if page < 0:
        page = pages_count
    elif page > pages_count:
        page = 0

    start = page * page_size
    end = start + page_size

    markup_buttons.append([types.InlineKeyboardButton(text="➕ Добавить сообщение", callback_data="add_saved_text")])

    for index, text_message in enumerate(texts[start:end]):
        emoji_status = "✅" if text_message['text'] in user_messages[user_id].get('text', []) else "❌"
        markup_buttons.append([types.InlineKeyboardButton(text=f"{emoji_status} {index + 1}.", callback_data="pass"),
                                types.InlineKeyboardButton(text=f"{text_message['text']}", callback_data=f"select_text_from_list:{text_message['id']}:{page}"),
                                 types.InlineKeyboardButton(text="🗑", callback_data=f"delete_saved_text:{text_message['id']}")])
        
    markup_buttons.append([types.InlineKeyboardButton(text=f"◀️", callback_data=f"select_message_from_list:{page - 1}"),
                            types.InlineKeyboardButton(text=f"{page+1}/{pages_count+1}", callback_data="pass"),
                                types.InlineKeyboardButton(text=f"▶️", callback_data=f"select_message_from_list:{page + 1}")])

    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_start_send_message")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("🔽 *Выберите сообщение:*",
                                    parse_mode="Markdown", reply_markup=markup)


@dp.callback_query(lambda call: call.data == "add_saved_text")
async def add_saved_text(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = "add_saved_text"

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="select_message_from_list")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("✏️ *Введите текст сообщения:*",
                                    parse_mode="Markdown", reply_markup=markup)
    

@dp.message(lambda message: user_states.get(message.from_user.id) == "add_saved_text")
async def add_saved_text(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = None

    await database.insert_saved_text(message.text)

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="select_message_from_list")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await message.answer("✅ *Сообщение успешно добавлено!*", parse_mode="Markdown", reply_markup=markup)


@dp.callback_query(lambda call: call.data.startswith("delete_saved_text:"))
async def delete_saved_text(call: types.CallbackQuery):
    text_id = int(call.data.split(":")[-1])
    await database.delete_saved_text(text_id)

    await select_message_from_list(call)
