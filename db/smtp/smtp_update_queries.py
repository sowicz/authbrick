from db.database import Database


async def update_smtp_config(config_id: str, **fields):
    if not fields:
        return

    keys = list(fields.keys())
    set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(keys)])

    query = f"""
        UPDATE smtp_config
        SET {set_clause}
        WHERE id = ${len(keys) + 1}
    """
    values = list(fields.values())
    values.append(config_id)

    await Database.execute(query, *values)