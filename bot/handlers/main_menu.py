from aiogram import types
from aiogram.filters import Command

import config
from bot import dp, user_states
from modules import database, userbot


async def generate_main_menu_markup(active_account: str, page=0) -> types.ReplyKeyboardMarkup:
    markup_buttons = []

    if not active_account:
        return None

    chats = await userbot.get_chats(active_account)

    page_size = 7
    pages_count = (len(chats) - 1) // page_size

    if page < 0:
        page = 0
    elif page > pages_count:
        page = pages_count

    start = page * page_size
    end = start + page_size

    markup_buttons.append([types.InlineKeyboardButton(text="🔄 Обновить чаты", callback_data=f"update_list:{active_account}"),
                            types.InlineKeyboardButton(text="🌐 Изменить прокси", callback_data=f"change_proxy:{active_account}")])

    for chat in chats[start:end]:
        emoji_status = "❌" if chat.id not in userbot.selected_chats[active_account] else "✅"
        markup_buttons.append([types.InlineKeyboardButton(text=f"{emoji_status} {chat.title} {emoji_status}", callback_data=f"select_chat:{chat.id}:{page}")])

    markup_buttons.append([types.InlineKeyboardButton(text=f"◀️", callback_data=f"show_chats:{page - 1}"),
                            types.InlineKeyboardButton(text=f"{page+1}/{pages_count+1}", callback_data="pass"),
                             types.InlineKeyboardButton(text=f"▶️", callback_data=f"show_chats:{page + 1}")])

    markup_buttons.append([types.InlineKeyboardButton(text="👤 Изменить аккаунт", callback_data="change_account")])
    markup_buttons.append([types.InlineKeyboardButton(text="📢 Отправить сообщение", callback_data="start_send_message")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    return markup


async def handle_main_menu(event_data, page=0):
    user_id = event_data.from_user.id
    user_states[user_id] = None

    user = await database.get_user(user_id)
    if not user:
        if user_id in config.ADMINS:
            await database.insert_user(user_id, event_data.from_user.username, event_data.from_user.first_name)
        else:
            if isinstance(event_data, types.Message):
                await event_data.answer("❌ *Доступ запрещен!*", parse_mode="Markdown")
            elif isinstance(event_data, types.CallbackQuery):
                await event_data.message.answer("❌ *Доступ запрещен!*", parse_mode="Markdown")
                await event_data.message.delete()
            return
    elif user["username"] != event_data.from_user.username or user["first_name"] != event_data.from_user.first_name:
        await database.update_user(user_id, "username", event_data.from_user.username)
        await database.update_user(user_id, "first_name", event_data.from_user.first_name)

    active_account = userbot.active_accounts.get(user_id)
    if not active_account:
        markup_buttons = []
        accounts = await database.get_authorized_accounts()

        if not accounts:
            if isinstance(event_data, types.Message):
                await event_data.answer("❌ *Аккаунты не найдены! Добавьте аккаунт запустив скрипт 'login.py'.*", parse_mode="Markdown")
            elif isinstance(event_data, types.CallbackQuery):
                await event_data.message.edit_text("❌ *Аккаунты не найдены! Добавьте аккаунт запустив скрипт 'login.py'.*", parse_mode="Markdown")
            return

        for account in accounts:
            markup_buttons.append([types.InlineKeyboardButton(text=f"👤 {account['first_name']}", callback_data=f"select_active_account:{account['user_id']}")])

        markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

        if isinstance(event_data, types.Message):
            await event_data.answer("🔽 *Выберите аккаунт:*",
                                    parse_mode="Markdown", reply_markup=markup)
        elif isinstance(event_data, types.CallbackQuery):
            await event_data.message.edit_text("🔽 *Выберите аккаунт:*",
                                               parse_mode="Markdown", reply_markup=markup)
        return
    
    try:
        markup = await generate_main_menu_markup(active_account, page)
    except Exception as e:
        if 'Account is not authorized' in str(e):
            if isinstance(event_data, types.Message):
                await event_data.answer("❌ *Аккаунт не авторизован! Пожалуйста, авторизуйтесь заново.*", parse_mode="Markdown")
            elif isinstance(event_data, types.CallbackQuery):
                await event_data.message.edit_text("❌ *Аккаунт не авторизован! Пожалуйста, авторизуйтесь заново.*", parse_mode="Markdown")
            return
        elif "Connection error" in str(e):
            markup_buttons = []

            markup_buttons.append([types.InlineKeyboardButton(text="🌐 Изменить прокси", callback_data=f"change_proxy:{active_account}"),
                                    types.InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_account:{active_account}")])
            
            markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

            if isinstance(event_data, types.Message):
                await event_data.answer(f"❌ *Не удалось установить соединение с серверами телеграм.*\n\n"
                                        f"🔽 _Выберите действие:_", parse_mode="Markdown", reply_markup=markup)
            elif isinstance(event_data, types.CallbackQuery):
                await event_data.message.edit_text(f"❌ *Не удалось установить соединение с серверами телеграм.*\n\n"
                                                   f"🔽 _Выберите действие:_", parse_mode="Markdown", reply_markup=markup)
            return
        else:
            if isinstance(event_data, types.Message):
                await event_data.answer(f"❌ *Произошла ошибка при загрузке списка чатов!*\n\n`{e}`", parse_mode="Markdown")
            elif isinstance(event_data, types.CallbackQuery):
                await event_data.message.edit_text(f"❌ *Произошла ошибка при загрузке списка чатов!*\n\n`{e}`", parse_mode="Markdown")
            return
    
    selected_account = await database.get_user(int(active_account))

    if selected_account['proxy_data']:
        message_text = f"👤 *Активный аккаунт:* `{selected_account['first_name']}`\n" \
                    f"🌐 *Прокси:* `{selected_account['proxy_data']}`\n\n" \
                    f"🔽 _Выберите чаты:_"
    else:
        message_text = f"👤 *Активный аккаунт:* `{selected_account['first_name']}`\n\n" \
                        f"🔽 _Выберите чаты:_"

    if isinstance(event_data, types.Message):
        await event_data.answer(message_text, parse_mode="Markdown", reply_markup=markup)
    elif isinstance(event_data, types.CallbackQuery):
        try:
            await event_data.message.edit_text(message_text, parse_mode="Markdown", reply_markup=markup)
        except:
            pass


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await handle_main_menu(message)
    
    
@dp.callback_query(lambda call: call.data.startswith("show_chats:"))
async def show_chats(call: types.CallbackQuery):
    page = call.data.split(":")[-1]
    await handle_main_menu(call, int(page))


@dp.callback_query(lambda call: call.data == "main_menu")
async def main_menu(call: types.CallbackQuery):
    await handle_main_menu(call)


@dp.callback_query(lambda call: call.data.startswith("update_list:"))
async def update_list(call: types.CallbackQuery):
    await call.answer("⏳ Подождите...")

    try:
        active_account = call.data.split(":")[-1]
        await userbot.update_chat_list(active_account)
        await handle_main_menu(call)
    except Exception as e:
        await call.message.answer(f"❌ *Произошла ошибка при обновлении списка чатов!*\n\n`{e}`", parse_mode="Markdown")
        return