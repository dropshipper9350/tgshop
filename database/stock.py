from database.db import get_db


async def add_account(product_id, email, password, twofa_secret):

    db = await get_db()

    await db.execute(
        """
        INSERT INTO accounts
        (
            product_id,
            email,
            password,
            twofa_secret
        )
        VALUES
        (?,?,?,?)
        """,
        (
            product_id,
            email,
            password,
            twofa_secret

        )
    )

    await db.commit()

    await db.close()


async def get_stock_count(product_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT COUNT(*)
        FROM accounts
        WHERE status='available'
        AND product_id=?
        """,
        (product_id,)
    )

    count = (await cursor.fetchone())[0]

    await db.close()

    return count


async def get_total_stock_count():

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT COUNT(*)
        FROM accounts
        WHERE status='available'
        """
    )

    count = (await cursor.fetchone())[0]

    await db.close()

    return count

async def get_available_account(product_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT
            id,
            email,
            password,
            twofa_secret
        FROM accounts
        WHERE product_id=?
        AND status='available'
        LIMIT 1
        """,
        (product_id,)
    )

    account = await cursor.fetchone()

    await db.close()

    return account

async def claim_account(product_id):
    """
    Finds an available account and marks it sold in a way that's safe
    even if two approvals happen at nearly the same time.
    Returns the account row, or None if nothing was available/claimed.
    """

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT id, email, password, twofa_secret
        FROM accounts
        WHERE product_id=?
        AND status='available'
        LIMIT 1
        """,
        (product_id,)
    )

    account = await cursor.fetchone()

    if account is None:
        await db.close()
        return None

    account_id = account[0]

    result = await db.execute(
        """
        UPDATE accounts
        SET status='sold'
        WHERE id=? AND status='available'
        """,
        (account_id,)
    )

    await db.commit()

    claimed = result.rowcount == 1

    await db.close()

    if not claimed:
        # Someone else grabbed this exact account first — caller should retry
        return None

    return account


async def mark_account_sold(account_id):

    db = await get_db()

    await db.execute(
        """
        UPDATE accounts
        SET status='sold'
        WHERE id=?
        """,
        (
            account_id,
        )
    )

    await db.commit()

    await db.close()


async def account_exists(email):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT id
        FROM accounts
        WHERE email=?
        """,
        (email,)
    )

    account = await cursor.fetchone()

    await db.close()

    return account is not None