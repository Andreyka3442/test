from aiogram import Bot, Dispatcher

import config

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher()

user_states = {}