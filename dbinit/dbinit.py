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

    # =========================
    # Refresh tokens table
    # =========================

    cur.execute("""
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

        user_id UUID NOT NULL,
        token_hash TEXT NOT NULL,

        user_agent TEXT,
        ip_address TEXT,

        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        expires_at TIMESTAMPTZ NOT NULL,

        revoked BOOLEAN NOT NULL DEFAULT FALSE,

        CONSTRAINT fk_refresh_user
            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
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


    # =========================
    # SMTP configuration table
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS smtp_config (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

        smtp_host TEXT NOT NULL,
        smtp_port INTEGER NOT NULL CHECK (smtp_port > 0),

        smtp_user TEXT NOT NULL,
        smtp_password TEXT NOT NULL, -- encrypted

        from_email TEXT NOT NULL,

        use_tls BOOLEAN NOT NULL DEFAULT TRUE,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,

        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """)

    # =========================
    # MFA purpose enum
    # =========================
    cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'mfa_purpose'
        ) THEN
            CREATE TYPE mfa_purpose AS ENUM (
                'mfa',
                'password_reset',
                'email_verification'
            );
        END IF;
    END
    $$;
    """)

    # =========================
    # MFA codes table
    # =========================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mfa_codes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        code_hash TEXT NOT NULL,

        purpose mfa_purpose NOT NULL,

        expires_at TIMESTAMPTZ NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),

        created_at TIMESTAMPTZ DEFAULT now()
    );
    """)


    cur.close()
    conn.close()
    print("✅ Database initialized successfully")


if __name__ == "__main__":
    initialize()
