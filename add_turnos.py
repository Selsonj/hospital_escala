import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE turnos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT
)
""")

conn.commit()
conn.close()