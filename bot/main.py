import asyncio
from aiogram.types import BotCommand

import handlers
from bot import dp, bot
from modules import database


async def main():
    await database.init_db()

    commands = [
        BotCommand(command="/start", description="🚀 Запустить бота")
    ]

    await bot.set_my_commands(commands)


    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())