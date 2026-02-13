import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
APP_DB_USER = os.getenv("APP_DB_USER")
APP_DB_PASSWORD = os.getenv("APP_DB_PASSWORD")

DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_NAME,
    "user": APP_DB_USER,
    "password": APP_DB_PASSWORD
}


def cleanup_refresh_tokens():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = """
        DELETE FROM refresh_tokens
        WHERE revoked = TRUE
           OR expires_at < NOW()
    """

    cur.execute(query)
    deleted_rows = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    print(f"[{datetime.now()}] Deleted {deleted_rows} refresh tokens.")


if __name__ == "__main__":
    cleanup_refresh_tokens()

