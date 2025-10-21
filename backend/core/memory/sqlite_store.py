"""
SQLite storage module for managing document chunks metadata.

This module provides functionality to store and retrieve metadata about document
chunks in a SQLite database, including content, source information, and timestamps.
"""

import sqlite3
from datetime import datetime


def init_db(path: str) -> None:
    """
    Initialize the SQLite database with the chunks table if it doesn't exist.
    
    This function creates the necessary database schema for storing document chunks
    metadata. The table includes fields for chunk content, document ID, source filename,
    and creation timestamp.
    
    Args:
        path (str): Path to the SQLite database file
        
    Note:
        This function is safe to call multiple times as it uses CREATE TABLE IF NOT EXISTS.
    """
    conn = sqlite3.connect(path)

    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS chunks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   doc_id TEXT,
                   content TEXT,
                   chunk_index INTEGER,
                   source_filename TEXT,
                   created_at TEXT,
                   session_id TEXT
                   )""")
    conn.commit()
    conn.close()


def insert_chunk(doc_id: str, content: str, chunk_index: int, source_filename: str, created_at: str, path: str) -> None:
    """
    Insert a single chunk record into the SQLite database.
    
    This function stores metadata about a document chunk including its content,
    position in the document, source file information, and creation timestamp.
    
    Args:
        doc_id (str): Unique identifier for the document
        content (str): The actual text content of the chunk
        chunk_index (int): Position of this chunk within the original document
        source_filename (str): Name of the source file this chunk came from
        created_at (str): ISO format timestamp of when the chunk was created
        path (str): Path to the SQLite database file
        
    Note:
        The created_at parameter is overridden with the current timestamp.
        This function opens and closes its own database connection.
    """
    # Override with current timestamp for consistency
    created_at = datetime.now().isoformat()

    db = sqlite3.connect(path)

    cursor = db.cursor()
    cursor.execute("""
                   INSERT INTO chunks (doc_id, content, chunk_index, source_filename, created_at)
                   VALUES (?, ?, ?, ?, ?)""", (doc_id, content, chunk_index, source_filename, created_at) )
    
    db.commit()
    db.close()