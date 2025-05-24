import sqlite3

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()


def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            poster_id INTEGER NOT NULL
        )
    ''')
    conn.commit()


def add_or_update_user(user_id, poster_id, name=None, phone=None):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute(
            "INSERT INTO users (user_id, name, phone, poster_id) VALUES (?, ?, ?, ?)",
            (user_id, name, phone, poster_id)
        )
    else:
        if name is not None:
            cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
        if phone is not None:
            cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
    conn.commit()


def get_user(user_id):
    cursor.execute("SELECT name, phone, poster_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return {
            "name": result[0],
            "phone": result[1],
            "poster_id": result[2],
        }
    return None


def get_user_by_poster_id(poster_id):
    cursor.execute("SELECT user_id, name, phone, poster_id FROM users WHERE poster_id = ?", (poster_id,))
    result = cursor.fetchone()
    if result:
        return {
            "user_id": result[0],
            "name": result[1],
            "phone": result[2],
            "poster_id": result[3],
        }
    return None
