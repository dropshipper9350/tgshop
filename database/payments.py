from database.db import get_db


async def create_payment(user_id, product_id, telegram_file_id, quantity=1):

    db = await get_db()

    cursor = await db.execute(
        """
        INSERT INTO payments
        (
            user_id,
            product_id,
            telegram_file_id,
            quantity,
            status
        )
        VALUES
        (?,?,?,?,?)
        """,
        (
            user_id,
            product_id,
            telegram_file_id,
            quantity,
            "pending"
        )
    )

    payment_id = cursor.lastrowid

    await db.commit()
    await db.close()

    return payment_id


async def approve_payment(payment_id):

    db = await get_db()

    await db.execute(
        """
        UPDATE payments
        SET status='approved'
        WHERE id=?
        """,
        (payment_id,)
    )

    await db.commit()
    await db.close()


async def reject_payment(payment_id):

    db = await get_db()

    await db.execute(
        """
        UPDATE payments
        SET status='rejected'
        WHERE id=?
        """,
        (payment_id,)
    )

    await db.commit()
    await db.close()


async def get_payment(payment_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT
            user_id,
            product_id,
            quantity
        FROM payments
        WHERE id=?
        """,
        (payment_id,)
    )

    payment = await cursor.fetchone()

    await db.close()

    return payment


async def is_payment_pending(payment_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT status
        FROM payments
        WHERE id=?
        """,
        (payment_id,)
    )

    row = await cursor.fetchone()

    await db.close()

    if row is None:
        return False

    return row[0] == "pending"


async def get_pending_count():

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT COUNT(*)
        FROM payments
        WHERE status='pending'
        """
    )

    total = (await cursor.fetchone())[0]

    await db.close()

    return total


async def get_pending_payments():

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT
            id,
            user_id,
            product_id,
            quantity
        FROM payments
        WHERE status='pending'
        ORDER BY id DESC
        """
    )

    payments = await cursor.fetchall()

    await db.close()

    return payments