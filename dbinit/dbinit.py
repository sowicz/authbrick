import os
import psycopg2
import hashlib
from psycopg2 import sql
from dotenv import load_dotenv
from passlib.context import CryptContext


load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

SUPERUSER = os.getenv("POSTGRES_USER")
SUPERUSER_PASSWORD = os.getenv("POSTGRES_PASSWORD")

APP_USER = os.getenv("APP_DB_USER")
APP_PASSWORD = os.getenv("APP_DB_PASSWORD")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# =========================
# Password hashing context
# =========================
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def initialize():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=SUPERUSER,
        password=SUPERUSER_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True
    cur = conn.cursor()

    # UUID support
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # =========================
    # Application DB role
    # =========================
    cur.execute(
        sql.SQL("""
        DO $$
        BEGIN
            IF EXISTS (SELECT FROM pg_roles WHERE rolname = {role}) THEN
                EXECUTE format('ALTER ROLE %I LOGIN PASSWORD %L', {role}, {password});
            ELSE
                EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', {role}, {password});
            END IF;
        END
        $$;
        """).format(
            role=sql.Literal(APP_USER),
            password=sql.Literal(APP_PASSWORD),
        )
    )

    # =========================
    # Permissions
    # =========================
    cur.execute(sql.SQL("""
        GRANT CONNECT ON DATABASE {db} TO {user};
        GRANT USAGE, CREATE ON SCHEMA public TO {user};
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {user};
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {user};
    """).format(
        db=sql.Identifier(DB_NAME),
        user=sql.Identifier(APP_USER),
    ))

    cur.execute(sql.SQL("""
        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT ALL ON TABLES TO {user};
    """).format(
        user=sql.Identifier(APP_USER),
    ))

    # =========================
    # Roles table
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY,
        role TEXT UNIQUE NOT NULL
    );
    """)


    cur.execute("""
    INSERT INTO roles (id, role) VALUES
        (0, 'root'),
        (1, 'admin'),
        (2, 'advanced'),
        (3, 'operator'),
        (4, 'client')
    ON CONFLICT (id) DO UPDATE
    SET role = EXCLUDED.role;
    """)


    # =========================
    # Users table
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,

        first_name TEXT,
        last_name TEXT,
        user_code TEXT,

        first_login BOOLEAN NOT NULL DEFAULT TRUE,
        last_pass_change TIMESTAMPTZ,

        mfa BOOLEAN NOT NULL DEFAULT FALSE,
        mfa_code INTEGER,

        role_id INTEGER NOT NULL DEFAULT 3,
        last_login TIMESTAMPTZ,

        created_at TIMESTAMPTZ DEFAULT now(),

        CONSTRAINT fk_role
            FOREIGN KEY (role_id)
            REFERENCES roles(id)
            ON DELETE RESTRICT
    );
    """)

    # User code unique index (only for non-null values)
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS ux_users_user_code
    ON users(user_code)
    WHERE user_code IS NOT NULL;
    """)

    # =========================
    # Seed admin user
    # =========================
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError("ADMIN_EMAIL / ADMIN_PASSWORD not set in .env")

    admin_password_hash = hash_password(ADMIN_PASSWORD)

    cur.execute("""
    INSERT INTO users (
        email,
        password,
        role_id,
        first_login
    )
    VALUES (%s, %s, 0, FALSE)
    ON CONFLICT (email) DO NOTHING;
    """, (
        ADMIN_EMAIL,
        admin_password_hash,
    ))


    cur.close()
    conn.close()
    print("✅ Database initialized successfully")


if __name__ == "__main__":
    initialize()
