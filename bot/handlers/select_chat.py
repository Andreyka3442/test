from aiogram import types

from bot import dp
from modules import userbot
from handlers.main_menu import handle_main_menu


@dp.callback_query(lambda call: call.data.startswith("select_chat:"))
async def select_chat(call: types.CallbackQuery):
    user_id = call.from_user.id
    chat_id = int(call.data.split(":")[-2])
    page = int(call.data.split(":")[-1])

    active_account = userbot.active_accounts[user_id]

    if chat_id in userbot.selected_chats[active_account]:
        userbot.selected_chats[active_account].remove(chat_id)
    else:
        userbot.selected_chats[active_account].append(chat_id)

    await handle_main_menu(call, page)