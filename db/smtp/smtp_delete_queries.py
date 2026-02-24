from db.database import Database


# async def delete_smtp_config():
#     query = "DELETE FROM smtp_config"
#     await Database.execute(query)

async def delete_smtp_config_by_id(config_id: str):
    query = """
        DELETE FROM smtp_config
        WHERE id = $1
    """
    return await Database.execute(query, config_id)