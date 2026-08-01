import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "users.db"


# =====================================
# Database Connection
# =====================================

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =====================================
# Validation Functions
# =====================================

def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_username(username):
    return (
        len(username) >= 3
        and username.replace("_", "").isalnum()
    )


def is_strong_password(password):
    return len(password) >= 8


# =====================================
# Create Users Table
# =====================================

def create_users_table():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                email TEXT UNIQUE NOT NULL,

                password TEXT NOT NULL

            )
        """)

        conn.commit()


# =====================================
# Register User
# =====================================

def register_user(username, email, password):

    username = username.strip()
    email = email.strip().lower()

    if not is_valid_username(username):
        return False

    if not is_valid_email(email):
        return False

    if not is_strong_password(password):
        return False

    hashed_password = generate_password_hash(password)

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (
                    username,
                    email,
                    password
                )
                VALUES
                (
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    username,
                    email,
                    hashed_password
                )
            )

            conn.commit()

            return True

    except sqlite3.IntegrityError:
        return False

    except sqlite3.Error as e:
        print("Database Error:", e)
        return False


# =====================================
# Login User
# =====================================

def login_user(email, password):

    email = email.strip().lower()

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password
                FROM users
                WHERE email = ?
                """,
                (email,)
            )

            user = cursor.fetchone()

            if user is None:
                return None

            if check_password_hash(user["password"], password):

                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                }

            return None

    except sqlite3.Error as e:

        print("Database Error:", e)
        return None


# =====================================
# Get User By ID
# =====================================

def get_user_by_id(user_id):

    try:

        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email
                FROM users
                WHERE id = ?
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if user is None:
                return None

            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }

    except sqlite3.Error as e:

        print("Database Error:", e)
        return None