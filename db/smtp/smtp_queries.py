from db.database import Database


async def insert_smtp_config(**data):
    query = """
        INSERT INTO smtp_config (
            smtp_host, smtp_port, smtp_user, smtp_password, 
            from_email, use_tls, is_active
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7);
    """
    await Database.execute(
        query, 
        data['smtp_host'], 
        data['smtp_port'], 
        data['smtp_user'], 
        data['smtp_password'], 
        data['from_email'], 
        data['use_tls'], 
        data['is_active']
    )


async def get_active_smtp():
    query = """
        SELECT *
        FROM smtp_config
        WHERE is_active = TRUE
        LIMIT 1
    """
    return await Database.fetchrow(query)
