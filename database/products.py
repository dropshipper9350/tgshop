from database.db import get_db


async def add_product(name, price, description):

    db = await get_db()

    cursor = await db.execute(
        """
        INSERT INTO products
        (
            name,
            price,
            description,
            active
        )
        VALUES
        (?,?,?,1)
        """,
        (
            name,
            price,
            description
        )
    )

    product_id = cursor.lastrowid

    await db.commit()
    await db.close()

    return product_id


async def get_all_products(active_only=False):

    db = await get_db()

    if active_only:
        cursor = await db.execute(
            """
            SELECT id, name, price, description, active
            FROM products
            WHERE active=1
            ORDER BY id
            """
        )
    else:
        cursor = await db.execute(
            """
            SELECT id, name, price, description, active
            FROM products
            ORDER BY id
            """
        )

    products = await cursor.fetchall()

    await db.close()

    return products


async def get_product(product_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT id, name, price, description, active
        FROM products
        WHERE id=?
        """,
        (product_id,)
    )

    product = await cursor.fetchone()

    await db.close()

    return product


async def set_product_active(product_id, active):

    db = await get_db()

    await db.execute(
        """
        UPDATE products
        SET active=?
        WHERE id=?
        """,
        (1 if active else 0, product_id)
    )

    await db.commit()
    await db.close()


async def delete_product(product_id):
    """
    Only deletes if no accounts were ever added for this product,
    so we never lose stock/order history by mistake.
    Returns True if deleted, False if it was blocked.
    """

    db = await get_db()

    cursor = await db.execute(
        "SELECT COUNT(*) FROM accounts WHERE product_id=?",
        (product_id,)
    )

    account_count = (await cursor.fetchone())[0]

    if account_count > 0:
        await db.close()
        return False

    await db.execute(
        "DELETE FROM products WHERE id=?",
        (product_id,)
    )

    await db.commit()
    await db.close()

    return True
