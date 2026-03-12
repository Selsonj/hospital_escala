import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
ALTER TABLE funcionarios
ADD COLUMN area_id INTEGER
""")

conn.commit()
conn.close()