import sqlite3
from datetime import datetime, timedelta


DATABASE = "elmo.db"


def get_connection():
    return sqlite3.connect(DATABASE)



def create_database():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        user_message TEXT,

        bot_response TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)


    conn.commit()
    conn.close()



# Save Chat

def save_message(user_id, user_message, bot_response):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO messages
    (
        user_id,
        user_message,
        bot_response
    )

    VALUES(?,?,?)
    """,
    (
        user_id,
        user_message,
        bot_response
    ))


    conn.commit()
    conn.close()



# Get History

def get_history(user_id):

    cleanup_old_memory()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
    SELECT user_message,
           bot_response

    FROM messages

    WHERE user_id=?

    ORDER BY id DESC

    LIMIT 10

    """,
    (user_id,))


    data = cursor.fetchall()

    conn.close()


    return [
        {
        "user_message":row[0],
        "bot_response":row[1]
        }
        for row in reversed(data)
    ]



# RAM CLEAR AFTER 3 DAYS

def cleanup_old_memory():

    conn=get_connection()

    cursor=conn.cursor()


    limit_date = datetime.now()-timedelta(days=3)


    cursor.execute("""
    DELETE FROM messages
    WHERE created_at < ?
    """,
    (limit_date,))


    conn.commit()

    conn.close()