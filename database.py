import sqlite3

DATABASE_NAME = "nutrify.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME, check_same_thread=False)

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profile(
id INTEGER PRIMARY KEY,
name TEXT,
age INTEGER,
gender TEXT,
height REAL,
weight REAL,
goal TEXT,
diet TEXT,
activity TEXT,
allergies TEXT,
medical TEXT,
calories INTEGER,
water_target INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
role TEXT,
message TEXT,
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS progress_logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT,
weight REAL,
calories INTEGER,
water INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS hydration(
id INTEGER PRIMARY KEY,
water INTEGER
)
""")

conn.commit()