import os
from aiogram import types

from bot import dp, user_states
from modules import database, userbot
from handlers.main_menu import handle_main_menu


@dp.callback_query(lambda call: call.data == "change_account")
async def change_account(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_states[user_id] = None

    markup_buttons = []
    accounts = await database.get_authorized_accounts()

    for index, account in enumerate(accounts):
        markup_buttons.append([types.InlineKeyboardButton(text=f"👤 {index + 1}.", callback_data="pass"),
                                types.InlineKeyboardButton(text=f"{account['first_name']}", callback_data=f"select_active_account:{account['user_id']}"),
                                 types.InlineKeyboardButton(text="🗑", callback_data=f"delete_account:{account['user_id']}")])

    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("🔽 *Выберите аккаунт:*",
                                    parse_mode="Markdown", reply_markup=markup)


@dp.callback_query(lambda call: call.data.startswith("select_active_account:"))
async def select_active_account(call: types.CallbackQuery):
    user_id = call.from_user.id
    userbot.active_accounts[user_id] = call.data.split(":")[-1]
    await handle_main_menu(call)


@dp.callback_query(lambda call: call.data.startswith("delete_account:"))
async def delete_account(call: types.CallbackQuery):
    account_id = int(call.data.split(":")[-1])

    await database.delete_user(account_id)

    for key, value in userbot.active_accounts.items():
        if value == str(account_id):
            userbot.active_accounts[key] = None

    os.remove(f"data/sessions/{account_id}.session")

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text("🗑 *Аккаунт успешно удален!*", reply_markup=markup, parse_mode="Markdown")