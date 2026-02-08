from db.database import Database


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


async def update_last_login(user_id):
    query = """
    UPDATE users
    SET last_login = now()
    WHERE id = $1
    """
    await Database.execute(query, user_id)
