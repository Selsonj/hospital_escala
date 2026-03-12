import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE escala (
id INTEGER PRIMARY KEY AUTOINCREMENT,
funcionario_id INTEGER,
data TEXT,
status TEXT
)
""")

conn.commit()
conn.close()