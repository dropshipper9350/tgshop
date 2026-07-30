from database.db import get_db


async def create_tables():
    db = await get_db()

    # Users
    await db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT
    )
    """)

    # Products
    await db.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        description TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    # Accounts (Stock)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    email TEXT,
    password TEXT,
    twofa_secret TEXT,
    status TEXT DEFAULT 'available'
)
""")

    # Orders
    await db.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        account_id INTEGER,
        status TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Payments
    await db.execute("""
    CREATE TABLE IF NOT EXISTS payments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    telegram_file_id TEXT,
    quantity INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # If the database already existed from before this feature was added,
    # the table above won't get the new column — add it here if missing.
    try:
        await db.execute(
            "ALTER TABLE payments ADD COLUMN quantity INTEGER DEFAULT 1"
        )
        await db.commit()
    except Exception:
        # Column already exists — that's fine, ignore
        pass

    await db.commit()

    # Insert ChatGPT Plus product if it doesn't exist
    cursor = await db.execute("SELECT COUNT(*) FROM products")
    count = (await cursor.fetchone())[0]

    if count == 0:
        await db.execute("""
        INSERT INTO products(name,price,description)
        VALUES(?,?,?)
        """, (
            "ChatGPT Plus",
            1.5,
            "30 Days Shared Account"
        ))

        await db.commit()

    await db.close()