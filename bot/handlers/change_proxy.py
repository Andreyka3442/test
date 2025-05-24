from aiogram import types

from bot import dp, user_states
from modules import database


@dp.callback_query(lambda call: call.data.startswith("change_proxy"))
async def change_proxy(call: types.CallbackQuery):
    user_id = call.from_user.id
    account_id = call.data.split(":")[-1]
    user_states[user_id] = f'new_proxy:{account_id}'

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await call.message.edit_text(f"🔽 *Введите новый прокси для аккаунта (ip:port:login:password), либо '-' если не хотите использовать прокси:*",
                                    parse_mode="Markdown", reply_markup=markup)
    

@dp.message(lambda message: user_states.get(message.from_user.id) and user_states.get(message.from_user.id).startswith('new_proxy:'))
async def new_proxy(message: types.Message):
    user_id = message.from_user.id
    account_id = int(user_states[user_id].split(":")[-1])

    if message.text != '-':
        parts = message.text.split(':')
        if len(parts) != 4:
            await message.answer("❌ *Неверный формат прокси! Попробуйте еще раз.*\n\n"
                                "🌐 `ip:port:login:password`", parse_mode="Markdown")
            return
        
        await database.update_user(account_id, 'proxy_data', message.text)
    else:
        await database.update_user(account_id, 'proxy_data', None)

    user_states[user_id] = None

    markup_buttons = []
    markup_buttons.append([types.InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])

    markup = types.InlineKeyboardMarkup(inline_keyboard=markup_buttons)

    await message.answer("✅ *Прокси успешно обновлен!*", parse_mode="Markdown", reply_markup=markup)