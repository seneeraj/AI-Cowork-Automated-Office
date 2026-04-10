import sqlite3
import uuid

DB_PATH = "memory.db"


class Memory:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        # Create all tables
        self.create_chat_tables()
        self.create_booking_table()
        self.create_activity_table()

    # =========================================================
    # CHAT TABLES
    # =========================================================
    def create_chat_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            name TEXT DEFAULT ''
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            chat_id TEXT,
            role TEXT,
            content TEXT
        )
        """)

        self.conn.commit()

    # =========================================================
    # BOOKINGS TABLE
    # =========================================================
    def create_booking_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            space TEXT,
            date TEXT,
            time TEXT
        )
        """)
        self.conn.commit()

    # =========================================================
    # ACTIVITY TABLE
    # =========================================================
    def create_activity_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            activity TEXT,
            timestamp TEXT
        )
        """)
        self.conn.commit()

    # =========================================================
    # CHAT FUNCTIONS
    # =========================================================
    def create_chat(self):
        chat_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO chats (id, name) VALUES (?, '')",
            (chat_id,)
        )
        self.conn.commit()
        return chat_id

    def get_chat_titles(self):
        return self.conn.execute(
            "SELECT id, name FROM chats"
        ).fetchall()

    def rename_chat(self, chat_id, new_name):
        self.conn.execute(
            "UPDATE chats SET name=? WHERE id=?",
            (new_name, chat_id)
        )
        self.conn.commit()

    def delete_chat(self, chat_id):
        self.conn.execute("DELETE FROM chats WHERE id=?", (chat_id,))
        self.conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
        self.conn.execute("DELETE FROM bookings WHERE chat_id=?", (chat_id,))
        self.conn.execute("DELETE FROM activity WHERE chat_id=?", (chat_id,))
        self.conn.commit()

    # =========================================================
    # MESSAGES
    # =========================================================
    def save_message(self, chat_id, role, content):
        self.conn.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content)
        )
        self.conn.commit()

    def get_messages(self, chat_id):
        rows = self.conn.execute(
            "SELECT role, content FROM messages WHERE chat_id=?",
            (chat_id,)
        ).fetchall()

        return [{"role": r[0], "content": r[1]} for r in rows]

    def get_recent_context(self, chat_id, limit=5):
        rows = self.conn.execute(
            "SELECT role, content FROM messages WHERE chat_id=? ORDER BY rowid DESC LIMIT ?",
            (chat_id, limit)
        ).fetchall()

        rows = rows[::-1]

        context = ""
        for r in rows:
            context += f"{r[0]}: {r[1]}\n"

        return context

    # =========================================================
    # BOOKINGS
    # =========================================================
    def save_booking(self, chat_id, space, date, time):
        self.conn.execute(
            "INSERT INTO bookings (chat_id, space, date, time) VALUES (?, ?, ?, ?)",
            (chat_id, space, date, time)
        )
        self.conn.commit()

    def get_bookings(self, chat_id):
        return self.conn.execute(
            "SELECT space, date, time FROM bookings WHERE chat_id=?",
            (chat_id,)
        ).fetchall()

    def delete_booking(self, chat_id, space, date, time):
        self.conn.execute(
            "DELETE FROM bookings WHERE chat_id=? AND space=? AND date=? AND time=?",
            (chat_id, space, date, time)
        )
        self.conn.commit()

    # =========================================================
    # ACTIVITY
    # =========================================================
    def save_activity(self, chat_id, activity):
        self.conn.execute(
            "INSERT INTO activity (chat_id, activity, timestamp) VALUES (?, ?, datetime('now'))",
            (chat_id, activity)
        )
        self.conn.commit()

    def get_activities(self, chat_id):
        rows = self.conn.execute(
            "SELECT activity FROM activity WHERE chat_id=? ORDER BY id DESC LIMIT 5",
            (chat_id,)
        ).fetchall()

        return [r[0] for r in rows]