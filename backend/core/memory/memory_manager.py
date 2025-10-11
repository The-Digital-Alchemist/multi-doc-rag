import faiss
import sqlite3
import os
import numpy as np
from datetime import datetime
from core.memory.sqlite_store import init_db
from core.memory.faiss_store import build_faiss_index

class MemoryManager:
    def __init__(self, faiss_path: str, sqlite_path: str):

        self.faiss_path = faiss_path
        self.sqlite_path = sqlite_path

        init_db(sqlite_path)
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.row_factory = sqlite3.Row
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

        if os.path.exists(faiss_path):
            self.index = faiss.read_index(faiss_path)

        else:
            self.index = None



    def add_document(self, chunks: list[str], embeddings: np.ndarray, doc_id: str, source_filename: str):

        cursor = self.conn.cursor()
        chunks_ids = []
        

        for idx, chunk in enumerate(chunks):
            created_at = datetime.now().isoformat()
            cursor.execute("""
            INSERT INTO chunks (doc_id, content, chunk_index, source_filename, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (doc_id, chunk, idx, source_filename, created_at))
            chunks_ids.append(cursor.lastrowid)
            
            
        self.conn.commit()

        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        if self.index is None:
            d = embeddings.shape[1]
            self.index = faiss.IndexIDMap(faiss.IndexFlatIP(d))

        self.index.add_with_ids(embeddings, np.array(chunks_ids, dtype=np.int64)) #type: ignore

        self.save_index()


    def search(self, query_vector: np.ndarray, k: int = 3):

        if self.index is None:
            print("Index not loaded in memory. Attempting to reload..")
            self.load_index()
            if self.index is None:
                raise ValueError("Failed to load index. Ensure /upload was called first.")
        
        q = np.asarray(query_vector, dtype=np.float32)
        if q.ndim == 1:
            q = q [None, :]

        faiss.normalize_L2(q)

        distances, ids = self.index.search(q, k) # type: ignore
        id_list = [int(i) for i in ids[0] if i != -1]
        score_list = [float(s) for i, s in zip(ids[0], distances[0]) if i != -1]

        if not id_list:
            return[]

        placeholders = ",".join("?" for _ in id_list)
        rows = self.conn.execute(f"""
                           SELECT id, doc_id, content, source_filename FROM chunks WHERE id IN ({placeholders})
                           """, id_list).fetchall()


        by_id = {row["id"]: row for row in rows}
        results = []

        for cid, score in zip(id_list, score_list):
            row = by_id.get(cid)
            if row:
                results.append({
                    "id": cid,
                    "score": score,
                    "doc_id": row["doc_id"],
                    "content": row["content"],
                    "source_filename": row["source_filename"],
                })
        return results
                    
    def save_index(self):
        if self.index is not None:
            faiss.write_index(self.index, self.faiss_path)


    def load_index(self):
        if os.path.exists(self.faiss_path):
            try:
                self.index = faiss.read_index(self.faiss_path)
                print("FAISS index successfully loaded from disk.")
            except Exception as e:
                print(f"Failed to load FAISS index: {e}. Reinitializing new index.")
                self.index = None
        else:
            print("No FAISS index found, creating new.")
            self.index = None

    