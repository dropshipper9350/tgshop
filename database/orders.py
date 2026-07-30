from database.db import get_db


async def create_order(user_id, product_id, account_id):

    db = await get_db()

    await db.execute(
        """
        INSERT INTO orders
        (
            user_id,
            product_id,
            account_id,
            status
        )
        VALUES
        (?,?,?,?)
        """,
        (
            user_id,
            product_id,
            account_id,
            "completed"
        )
    )

    await db.commit()
    await db.close()


async def get_orders_by_user(user_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT
            orders.status,
            orders.created,
            products.name
        FROM orders
        LEFT JOIN products ON products.id = orders.product_id
        WHERE orders.user_id=?
        ORDER BY orders.id DESC
        """,
        (user_id,)
    )

    rows = await cursor.fetchall()

    await db.close()

    return rows


async def get_total_orders():

    db = await get_db()

    cursor = await db.execute(
        "SELECT COUNT(*) FROM orders"
    )

    total = (await cursor.fetchone())[0]

    await db.close()

    return total


async def get_total_revenue():
    """
    Sums up the product price at each order, so total revenue stays
    accurate even if a product's price is changed later or you have
    several products with different prices.
    """

    db = await get_db()

    cursor = await db.execute("""
    SELECT COALESCE(SUM(products.price), 0)
    FROM orders
    LEFT JOIN products ON products.id = orders.product_id
    """)

    total = (await cursor.fetchone())[0]

    await db.close()

    return round(total, 2)


async def get_last_orders(limit=10):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT
            orders.user_id,
            products.name,
            orders.created
        FROM orders
        LEFT JOIN products ON products.id = orders.product_id
        ORDER BY orders.id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = await cursor.fetchall()

    await db.close()

    return rows
