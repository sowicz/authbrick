from db.database import Database


async def delete_smtp_config():
    query = "DELETE FROM smtp_config"
    await Database.execute(query)
