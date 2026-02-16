from db.database import Database



async def update_last_login(user_id):
    query = """
        UPDATE users
        SET last_login = now()
        WHERE id = $1
    """
    await Database.execute(query, user_id)



async def disable_first_login(user_id: str):
    query = """
        UPDATE users
        SET first_login = FALSE,
            last_pass_change = now()
        WHERE id = $1
    """
    await Database.execute(query, user_id)


async def is_first_login(user_id: str) -> bool:
    query = """
        SELECT first_login
        FROM users
        WHERE id = $1
    """
    result = await Database.fetchrow(query, user_id)
    return result["first_login"] if result else False


async def update_user_password(user_id: str, hashed_password: str):
    query = """
        UPDATE users
        SET password = $2,
            first_login = FALSE,
            last_pass_change = now()
        WHERE id = $1
    """
    await Database.execute(query, user_id, hashed_password)


async def revoke_refresh_token(token_hash: str):
    query = """
        UPDATE refresh_tokens
        SET revoked = TRUE
        WHERE token_hash = $1
    """
    await Database.execute(query, token_hash)



async def revoke_all_user_refresh_tokens(user_id: str):
    query = """
        UPDATE refresh_tokens
        SET revoked = TRUE
        WHERE user_id = $1
    """
    await Database.execute(query, user_id)

