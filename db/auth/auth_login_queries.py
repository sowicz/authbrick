from db.database import Database
from datetime import datetime, timedelta


REFRESH_TOKEN_EXPIRE_DAYS = 1


async def get_user_by_email(email: str):
    query = """
    SELECT
        id,
        email,
        password,
        role_id,
        first_login
    FROM users
    WHERE email = $1
    """
    return await Database.fetchrow(query, email)


async def get_user_by_id(user_id: str):
    query = """
        SELECT
            id,
            email,
            password,
            role_id,
            first_login,
            last_login,
            created_at
        FROM users
        WHERE id = $1
        LIMIT 1
    """
    return await Database.fetchrow(query, user_id)





async def save_refresh_token(
    user_id: str,
    token_hash: str,
    user_agent: str | None,
    ip_address: str | None,
):
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # delete old token for the same user and user agent
    delete_query = """
        DELETE FROM refresh_tokens
        WHERE user_id = $1
        AND user_agent = $2
        AND revoked = FALSE
    """

    await Database.execute(delete_query, user_id, user_agent)

    #  save new token
    insert_query = """
        INSERT INTO refresh_tokens (
            user_id,
            token_hash,
            user_agent,
            ip_address,
            expires_at
        )
        VALUES ($1, $2, $3, $4, $5)
    """

    await Database.execute(
        insert_query,
        user_id,
        token_hash,
        user_agent,
        ip_address,
        expires_at,
    )


async def get_valid_refresh_token(token_hash: str):
    query = """
        SELECT *
        FROM refresh_tokens
        WHERE token_hash = $1
        AND revoked = FALSE
        AND expires_at > now()
        LIMIT 1
    """
    return await Database.fetchrow(query, token_hash)


