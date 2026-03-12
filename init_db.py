import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE funcionarios (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
funcao TEXT,
departamento TEXT
)
""")

conn.commit()
conn.close()