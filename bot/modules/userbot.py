import os
import asyncio
from telethon import TelegramClient, functions
from telethon.errors.rpcerrorlist import AccessTokenExpiredError, AuthKeyInvalidError, AuthTokenExpiredError, FloodWaitError
from telethon.tl.types import Chat, Channel
from datetime import datetime, timedelta

import config
from modules import database

active_accounts = {}
user_chats = {}
selected_chats = {}

async def create_client(session_name: str):
    db_account = await database.get_user(int(session_name))
    if not db_account:
        raise Exception("Account is not authorized")
    
    if db_account['proxy_data']:
        proxy_ip, proxy_port, proxy_login, proxy_password = db_account['proxy_data'].split(":")
        proxy = {
            "ip": proxy_ip,
            "port": proxy_port,
            "login": proxy_login,
            "password": proxy_password
        }
    else:
        proxy = None


    client = TelegramClient(
        session = f"data/sessions/{session_name}",
        api_id = config.API_ID,
        api_hash = config.API_HASH,
        system_version = config.SYSTEM_VERSION,
        app_version = config.APP_VERSION,
        lang_code = config.LANG_CODE,
        device_model = config.DEVICE_MODEL,
        proxy = ("socks5", proxy['ip'], int(proxy['port']), True, proxy['login'], proxy['password']) if proxy else None,
        connection_retries=0
    )

    return client


async def get_me(session_name: str):
    client = await create_client(session_name)

    try:
        await client.start()

        me = await client.get_me()
    except (AccessTokenExpiredError, AuthKeyInvalidError, AuthTokenExpiredError):
        if client.is_connected():
            await client.disconnect()

        print(f"[Account is not authorized] {session_name}")
        os.remove(f"data/sessions/{session_name}.session")
        await database.delete_user(int(session_name))
        for user_id in active_accounts:
            if active_accounts[user_id] == session_name:
                del active_accounts[user_id]

        raise Exception("Account is not authorized")
    except Exception as e:
        if "The user has been deleted/deactivated" in str(e):
            if client.is_connected():
                await client.disconnect()

            print(f"[User has been deleted/deactivated] {session_name}")
            os.remove(f"data/sessions/{session_name}.session")
            await database.delete_user(int(session_name))
            for user_id in active_accounts:
                if active_accounts[user_id] == session_name:
                    del active_accounts[user_id]

            raise Exception("Account is not authorized")
        else:
            print(f"[Error when trying to get me] {e}")
            raise Exception("Error when trying to get me")
    finally:
        if client.is_connected():
            await client.disconnect()

    return me


async def get_chats(session_name: str):
    if session_name in user_chats:
        return user_chats[session_name]

    return await update_chat_list(session_name)


async def update_chat_list(session_name: str):
    client = await create_client(session_name)

    try:
        await client.start()

        dialogs = await client(functions.messages.GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=0,
            limit=500,
            hash=0
        ))
    except (AccessTokenExpiredError, AuthKeyInvalidError, AuthTokenExpiredError):
        if client.is_connected():
            await client.disconnect()

        print(f"[Account is not authorized] {session_name}")
        os.remove(f"data/sessions/{session_name}.session")
        await database.delete_user(int(session_name))
        for user_id in active_accounts:
            if active_accounts[user_id] == session_name:
                del active_accounts[user_id]

        raise Exception("Account is not authorized")
    except Exception as e:
        if "The user has been deleted/deactivated" in str(e):
            if client.is_connected():
                await client.disconnect()

            print(f"[User has been deleted/deactivated] {session_name}")
            os.remove(f"data/sessions/{session_name}.session")
            await database.delete_user(int(session_name))
            for user_id in active_accounts:
                if active_accounts[user_id] == session_name:
                    del active_accounts[user_id]

            raise Exception("Account is not authorized")
        elif "Connection to Telegram failed" in str(e):
            if client.is_connected():
                await client.disconnect()

            print(f"[Connection error] {session_name}")
            raise Exception("Connection error")
        else:
            print(f"[Error when trying to get dialogs] {e}")
            raise Exception("Error when trying to get dialogs")
    finally:
        if client.is_connected():
            await client.disconnect()

    groups = [d for d in dialogs.chats if isinstance(d, Chat) or isinstance(d, Channel)]

    user_chats[session_name] = groups
    selected_chats[session_name] = []
    return user_chats[session_name]


async def send_delay_messages(session_name: str, chat_id: int, texts: str, minutes: int, count: int):
    client = await create_client(session_name)

    chat_title = "Unknown"
    success_count = 0
    error_count = 0

    try:
        await client.start()
        
        chat_entity = await client.get_entity(chat_id)
        chat_title = chat_entity.title

        for i in range(count):
            try:
                schedule_time = datetime.utcnow() + timedelta(minutes=minutes * (i + 1))

                text = texts[i % len(texts)]

                await client.send_message(chat_entity, text, schedule=schedule_time)
                success_count += 1
            except FloodWaitError as e:
                error_count += 1
                print(f"[FloodWaitError] {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
            except (AccessTokenExpiredError, AuthKeyInvalidError, AuthTokenExpiredError):
                error_count = -999
                success_count = -999

                print(f"[Account is not authorized] {session_name}")
                break
            except Exception as e:
                if "The user has been deleted/deactivated" in str(e):
                    error_count = -999
                    success_count = -999

                    print(f"[User has been deleted/deactivated] {session_name}")
                    break
                else:
                    error_count += 1
                    print(f"[Error] {e}")

            await asyncio.sleep(1)
    except (AccessTokenExpiredError, AuthKeyInvalidError, AuthTokenExpiredError):
        error_count = -999
        success_count = -999

        print(f"[Account is not authorized] {session_name}")
    except Exception as e:
        if "The user has been deleted/deactivated" in str(e):
            error_count = -999
            success_count = -999

            print(f"[User has been deleted/deactivated] {session_name}")
        else:
            print(f"[Error when trying to get chat entity] {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

    if success_count == -999 and error_count == -999:
        os.remove(f"data/sessions/{session_name}.session")
        await database.delete_user(int(session_name))
        for user_id in active_accounts:
            if active_accounts[user_id] == session_name:
                del active_accounts[user_id]

    return chat_title, success_count, error_count