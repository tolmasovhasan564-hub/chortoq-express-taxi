import aiosqlite
from datetime import datetime, timedelta

DB_NAME = "taxi_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                role TEXT DEFAULT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                user_id INTEGER PRIMARY KEY,
                phone TEXT,
                username TEXT,
                driver_photo TEXT,
                car_model TEXT,
                car_number TEXT,
                car_photo TEXT,
                balance REAL DEFAULT 0.0,
                is_approved INTEGER DEFAULT 0,
                status TEXT DEFAULT 'offline',
                active_route TEXT DEFAULT NULL,
                paid_until TIMESTAMP DEFAULT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                driver_id INTEGER DEFAULT NULL,
                pickup_location TEXT,
                dropoff_location TEXT,
                price TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def set_user_role(user_id: int, role: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)", (user_id, role))
        await db.commit()

async def get_user_role(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT role FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def register_driver(user_id: int, phone: str, username: str, driver_photo: str, car_model: str, car_number: str, car_photo: str):
    paid_until = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR REPLACE INTO drivers (user_id, phone, username, driver_photo, car_model, car_number, car_photo, status, active_route, paid_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'offline', NULL, ?)
        """, (user_id, phone, username, driver_photo, car_model, car_number, car_photo, paid_until))
        await db.commit()

async def get_driver(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM drivers WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def is_driver_paid(user_id: int) -> bool:
    driver = await get_driver(user_id)
    if not driver or not driver[11]:
        return False
    try:
        paid_until_dt = datetime.strptime(driver[11], "%Y-%m-%d %H:%M:%S")
        return datetime.now() < paid_until_dt
    except Exception:
        return False

async def renew_subscription(user_id: int, days: int = 7):
    driver = await get_driver(user_id)
    now = datetime.now()
    if driver and driver[11]:
        try:
            current_expiry = datetime.strptime(driver[11], "%Y-%m-%d %H:%M:%S")
            if current_expiry > now:
                now = current_expiry
        except Exception:
            pass
            
    new_expiry = (now + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE drivers SET paid_until = ? WHERE user_id = ?", (new_expiry, user_id))
        await db.commit()

async def update_driver_status(user_id: int, status: str, route: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE drivers SET status = ?, active_route = ? WHERE user_id = ?", (status, route, user_id))
        await db.commit()

async def get_online_drivers_by_route(route: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM drivers WHERE status = 'online' AND active_route = ?", (route,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def add_order(client_id: int, pickup: str, dropoff: str, price: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO orders (client_id, pickup_location, dropoff_location, price, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (client_id, pickup, dropoff, price))
        await db.commit()
        return cursor.lastrowid

async def assign_order(order_id: int, driver_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT status FROM orders WHERE id = ?", (order_id,)) as cursor:
            order = await cursor.fetchone()
            if not order or order[0] != 'pending':
                return False
        
        await db.execute("""
            UPDATE orders SET driver_id = ?, status = 'accepted' WHERE id = ?
        """, (driver_id, order_id))
        await db.commit()
        return True

async def get_order(order_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)) as cursor:
            return await cursor.fetchone()

async def cancel_order_db(order_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
        await db.commit()

