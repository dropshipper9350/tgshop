from database.db import get_db


async def add_user(user):

    db = await get_db()

    await db.execute(
        """
        INSERT OR IGNORE INTO users
        (
            user_id,
            username,
            full_name
        )
        VALUES
        (?,?,?)
        """,
        (
            user.id,
            user.username,
            user.full_name
        )
    )

    await db.commit()
    await db.close()


async def get_total_users():

    db = await get_db()

    cursor = await db.execute("""
    SELECT COUNT(*)
    FROM users
    """)

    total = (await cursor.fetchone())[0]

    await db.close()

    return total


async def get_all_users():

    db = await get_db()

    cursor = await db.execute("""
    SELECT
        user_id,
        full_name
    FROM users
    ORDER BY user_id DESC
    """)

    users = await cursor.fetchall()

    await db.close()

    return users
