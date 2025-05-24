import os
import asyncio
from telethon import TelegramClient

import config
from modules import database


async def main():
    await database.init_db()

    session_name = "new_session"

    if not os.path.exists("data/sessions"):
        os.makedirs("data/sessions")

    if os.path.exists(f"data/sessions/{session_name}.session"):
        os.remove(f"data/sessions/{session_name}.session")
    
    proxy_data = None
    while not proxy_data:
        proxy_data = input("Enter proxy (ip:port:login:password) or '-' if you don't want to use proxy: ")

        if proxy_data == "-":
            proxy = None
            proxy_data = None
            break

        parts = proxy_data.split(":")
        if len(parts) == 4:
            proxy_ip, proxy_port, proxy_login, proxy_password = parts
            proxy = {
                "ip": proxy_ip,
                "port": proxy_port,
                "login": proxy_login,
                "password": proxy_password
            }
        else:
            print("Invalid format. Please enter in the format ip:port:login:password")
            proxy_data = None

    client = TelegramClient(
        session = f"data/sessions/{session_name}.session",
        api_id = config.API_ID,
        api_hash = config.API_HASH,
        system_version = config.SYSTEM_VERSION,
        app_version = config.APP_VERSION,
        lang_code = config.LANG_CODE,
        device_model = config.DEVICE_MODEL,
        proxy = ("socks5", proxy['ip'], int(proxy['port']), True, proxy['login'], proxy['password']) if proxy else None
    )

    try:
        await client.start()
    except Exception as e:
        print(f"Authorization error: {e}")
        return
    
    me = await client.get_me()
    
    await database.insert_user(me.id, me.username, me.first_name, "authorized", proxy_data)
    
    print("You are authorized")
    await client.disconnect()

    os.rename(f"data/sessions/{session_name}.session", f"data/sessions/{me.id}.session")


if __name__ == "__main__":
    asyncio.run(main())