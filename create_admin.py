import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
INSERT INTO usuarios (username, password, role)
VALUES ('admin', 'admin123', 'admin')
""")

conn.commit()
conn.close()