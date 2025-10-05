import sqlite3
from datetime import datetime



def init_db(path: str):
    
    conn = sqlite3.connect(path)

    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS chunks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   doc_id TEXT,
                   content TEXT,
                   chunk_index INTEGER,
                   source_filename TEXT,
                   created_at TEXT
                   )""")
    conn.commit()
    conn.close()





def insert_chunk(doc_id, content, chunk_index, source_filename, created_at, path):

    created_at = datetime.now().isoformat()

    db = sqlite3.connect(path)

    cursor = db.cursor()
    cursor.execute("""
                   INSERT INTO chunks (doc_id, content, chunk_index, source_filename, created_at)
                   VALUES (?, ?, ?, ?, ?)""", (doc_id, content, chunk_index, source_filename, created_at) )
    

    db.commit()
    db.close()


