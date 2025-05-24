import aiosqlite


async def init_db():
    async with aiosqlite.connect('data/database/database.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                session_status TEXT DEFAULT "user",
                proxy_data TEXT,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS saved_texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()


async def insert_user(user_id, username, first_name, session_status="user", proxy_data=None):
    async with aiosqlite.connect('data/database/database.db') as db:
        await db.execute('''INSERT INTO users (user_id, username, first_name, session_status, proxy_data) VALUES (?, ?, ?, ?, ?)''', (user_id, username, first_name, session_status, proxy_data))
        await db.commit()


async def insert_saved_text(text):
    async with aiosqlite.connect('data/database/database.db') as db:
        await db.execute('''INSERT INTO saved_texts (text) VALUES (?)''', (text,))
        await db.commit()


async def update_user(user_id, column, value):
    async with aiosqlite.connect('data/database/database.db') as db:
        await db.execute(f'''UPDATE users SET {column} = ? WHERE user_id = ?''', (value, user_id))
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect('data/database/database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)) as cursor:
            return await cursor.fetchone()
        

async def get_all_users():
    async with aiosqlite.connect('data/database/database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''SELECT * FROM users''') as cursor:
            return await cursor.fetchall()
        
async def get_authorized_accounts():
    async with aiosqlite.connect('data/database/database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''SELECT * FROM users WHERE session_status = "authorized"''') as cursor:
            return await cursor.fetchall()
        

async def get_saved_text(text_id):
    async with aiosqlite.connect('data/database/database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''SELECT * FROM saved_texts WHERE id = ?''', (text_id,)) as cursor:
            return await cursor.fetchone()


async def get_saved_texts():
    async with aiosqlite.connect('data/database/database.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''SELECT * FROM saved_texts''') as cursor:
            return await cursor.fetchall()


async def delete_user(user_id):
    async with aiosqlite.connect('data/database/database.db') as db:
        await db.execute('''DELETE FROM users WHERE user_id = ?''', (user_id,))
        await db.commit()


async def delete_saved_text(text_id):
    async with aiosqlite.connect('data/database/database.db') as db:
        await db.execute('''DELETE FROM saved_texts WHERE id = ?''', (text_id,))
        await db.commit()