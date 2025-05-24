import telebot
from telebot import types
import json
import os
import time
from threading import Thread
from telebot.apihelper import ApiTelegramException

TOKEN = "7804091351:AAFrdNXGAc-8t0Ec0JUb3VlYAP3nmqimF5U"
ADMIN_ID = 6853344685
PROFILES_FILE = "profiles.json"
USERS_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)

if os.path.exists(PROFILES_FILE):
    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
        profiles = json.load(f)
else:
    profiles = []

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = set(json.load(f))
else:
    users = set()

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)

def save_profiles():
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

# Безопасная отправка сообщений
def safe_send_message(chat_id, text, **kwargs):
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except ApiTelegramException as e:
        if "bot was blocked by the user" in str(e) or "USER_IS_BLOCKED" in str(e):
            print(f"Пользователь {chat_id} заблокировал бота.")
        else:
            print(f"Ошибка при отправке сообщения: {e}")

# Безопасное удаление сообщений
def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except ApiTelegramException as e:
        if "message to delete not found" in str(e):
            print(f"Сообщение {message_id} уже удалено или не найдено.")
        else:
            print(f"Ошибка при удалении сообщения: {e}")

temp_adding = {}
last_profile_messages = {}

def cleanup_old_messages(chat_id):
    if chat_id in last_profile_messages:
        old_ids = last_profile_messages[chat_id]
        def delete_old():
            time.sleep(3)
            for msg_id in old_ids:
                safe_delete_message(chat_id, msg_id)
        Thread(target=delete_old).start()

@bot.message_handler(commands=['start'])
def start(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("💘 Найти девушку рядом"))
        markup.add(types.KeyboardButton("👩‍🦰 Посмотреть анкеты девушек"))
        if message.from_user.id == ADMIN_ID:
            markup.add(types.KeyboardButton("➕ Добавить анкету"))
            markup.add(types.KeyboardButton("🗑 Удалить анкету"))
        safe_send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в start: {e}")

@bot.message_handler(func=lambda msg: msg.text in ["💘 Найти девушку рядом", "👩‍🦰 Посмотреть анкеты девушек"])
def show_profile(message):
    try:
        users.add(message.from_user.id)
        save_users()
        if not profiles:
            safe_send_message(message.chat.id, "Анкет пока нет.")
        else:
            send_profile(message.chat.id, 0)
    except Exception as e:
        print(f"Ошибка в show_profile: {e}")

@bot.message_handler(func=lambda msg: msg.text == "➕ Добавить анкету")
def admin_add_profile(message):
    if message.from_user.id != ADMIN_ID:
        return safe_send_message(message.chat.id, "Доступ запрещён.")
    temp_adding[message.from_user.id] = {"description": "", "photos": []}
    safe_send_message(message.chat.id, "Отправь описание анкеты:")

@bot.message_handler(func=lambda msg: msg.text == "🗑 Удалить анкету")
def list_profiles_for_deletion(message):
    if message.from_user.id != ADMIN_ID:
        return safe_send_message(message.chat.id, "Доступ запрещён.")
    if not profiles:
        return safe_send_message(message.chat.id, "Анкет пока нет.")
    msg = "\n".join([f"{i+1}. {p['description'][:30]}..." for i, p in enumerate(profiles)])
    safe_send_message(message.chat.id, f"Список анкет:\n{msg}\n\nНапиши /delete НОМЕР для удаления.")

@bot.message_handler(commands=['delete'])
def delete_profile(message):
    if message.from_user.id != ADMIN_ID:
        return safe_send_message(message.chat.id, "Доступ запрещён.")
    try:
        index = int(message.text.split()[1]) - 1
        if 0 <= index < len(profiles):
            deleted = profiles.pop(index)
            save_profiles()
            safe_send_message(message.chat.id, f"Анкета удалена: {deleted['description'][:30]}...")
        else:
            safe_send_message(message.chat.id, "Неверный номер.")
    except Exception as e:
        safe_send_message(message.chat.id, "Формат команды: /delete НОМЕР")
        print(f"Ошибка в delete_profile: {e}")

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and msg.from_user.id in temp_adding and not temp_adding[msg.from_user.id]["description"])
def receive_description(message):
    temp_adding[message.from_user.id]["description"] = message.text
    safe_send_message(message.chat.id, "Отлично! Теперь отправляй фото. Когда закончишь — напиши /save")

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    if message.from_user.id in temp_adding and temp_adding[message.from_user.id]["description"]:
        temp_adding[message.from_user.id]["photos"].append(message.photo[-1].file_id)
        safe_send_message(message.chat.id, "Фото добавлено. Ещё фото или /save чтобы сохранить.")

@bot.message_handler(commands=['save'])
def save_profile(message):
    if message.from_user.id in temp_adding:
        profiles.append(temp_adding.pop(message.from_user.id))
        save_profiles()
        safe_send_message(message.chat.id, "Анкета сохранена ✅")
    else:
        safe_send_message(message.chat.id, "Нет данных для сохранения.")

def send_profile(chat_id, index):
    cleanup_old_messages(chat_id)

    profile = profiles[index]
    message_ids = []

    if profile["photos"]:
        media = [types.InputMediaPhoto(pid) for pid in profile["photos"]]
        try:
            sent = bot.send_media_group(chat_id, media)
            message_ids.extend([msg.message_id for msg in sent])
        except Exception as e:
            print(f"Ошибка при отправке фото: {e}")

    markup = types.InlineKeyboardMarkup()
    if index > 0:
        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data=f"profile_{index - 1}"))
    if index + 1 < len(profiles):
        markup.add(types.InlineKeyboardButton("➡ Далее", callback_data=f"profile_{index + 1}"))
    markup.add(types.InlineKeyboardButton("💋 Познакомиться", url="https://prev.affomelody.com/click?pid=98379&offer_id=25"))

    msg = safe_send_message(chat_id, profile["description"], reply_markup=markup)
    if msg:
        message_ids.append(msg.message_id)

    last_profile_messages[chat_id] = message_ids

@bot.callback_query_handler(func=lambda call: call.data.startswith("profile_"))
def navigate_profiles(call):
    try:
        index = int(call.data.split("_")[1])
        send_profile(call.message.chat.id, index)
    except Exception as e:
        print(f"Ошибка в navigate_profiles: {e}")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == ADMIN_ID:
        safe_send_message(message.chat.id, f"Всего пользователей: {len(users)}")
    else:
        safe_send_message(message.chat.id, "Доступ запрещён.")

def start_polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Глобальная ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_polling()
    auto-py-to-exe


