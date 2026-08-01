import sqlite3

DATABASE = "user_memory.db"


# =====================================
# Database Connection
# =====================================

def get_connection():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================
# Create Memory Table
# =====================================

def create_memory():

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profile (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    user_id INTEGER NOT NULL,

                    memory_key TEXT NOT NULL,

                    memory_value TEXT NOT NULL,

                    UNIQUE(user_id, memory_key)

                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_user
                ON profile(user_id)
            """)

            conn.commit()

    except sqlite3.Error as e:

        print(f"Memory Database Error: {e}")


# =====================================
# Save Memory
# =====================================

def save_memory(user_id, key, value):

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO profile
                (
                    user_id,
                    memory_key,
                    memory_value
                )

                VALUES (?, ?, ?)
            """,
            (
                user_id,
                key.strip(),
                value.strip()
            ))

            conn.commit()

            return True

    except sqlite3.Error as e:

        print(f"Save Memory Error: {e}")

        return False


# =====================================
# Get All Memory
# =====================================

def get_memory(user_id):

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    memory_key,
                    memory_value

                FROM profile

                WHERE user_id = ?
            """,
            (user_id,)
            )

            rows = cursor.fetchall()

            return {
                row["memory_key"]: row["memory_value"]
                for row in rows
            }

    except sqlite3.Error as e:

        print(f"Get Memory Error: {e}")

        return {}


# =====================================
# Get Single Memory
# =====================================

def get_memory_value(user_id, key):

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT memory_value

                FROM profile

                WHERE
                    user_id = ?
                    AND memory_key = ?
            """,
            (
                user_id,
                key
            ))

            row = cursor.fetchone()

            if row:
                return row["memory_value"]

            return None

    except sqlite3.Error:

        return None


# =====================================
# Delete Memory
# =====================================

def delete_memory(user_id, key):

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM profile

                WHERE
                    user_id = ?
                    AND memory_key = ?
            """,
            (
                user_id,
                key
            ))

            conn.commit()

            return True

    except sqlite3.Error as e:

        print(f"Delete Memory Error: {e}")

        return False


# =====================================
# Clear User Memory
# =====================================

def clear_memory(user_id):

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM profile

                WHERE user_id = ?
            """,
            (user_id,)
            )

            conn.commit()

            return True

    except sqlite3.Error as e:

        print(f"Clear Memory Error: {e}")

        return False