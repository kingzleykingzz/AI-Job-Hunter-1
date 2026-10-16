import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


DATABASE = "ai_job_hunter.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            plan TEXT NOT NULL DEFAULT 'free',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    connection.commit()

    connection.close()


def create_user(name, email, password):

    connection = get_connection()

    cursor = connection.cursor()

    hashed_password = generate_password_hash(
        password
    )

    try:

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, plan)
            VALUES (?, ?, ?, 'free')
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        connection.close()

        return user_id

    except sqlite3.IntegrityError:

        connection.close()

        return None


def get_user_by_email(email):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def verify_password(stored_password, password):

    return check_password_hash(
        stored_password,
        password
    )


def get_user_by_id(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def set_user_plan(user_id, plan):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET plan = ?
        WHERE id = ?
        """,
        (
            plan,
            user_id
        )
    )

    connection.commit()

    connection.close()