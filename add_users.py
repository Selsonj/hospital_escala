import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE usuarios (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
role TEXT,
area_id INTEGER
)
""")

conn.commit()
conn.close()