import faiss
import numpy as np




def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexIDMap:
    """
    A function that builds a FAISS vector index from a set of embeddings.
    """    
    dimension = embeddings.shape[1]
    index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))
    faiss.normalize_L2(embeddings)
    index.add_with_ids(embeddings, np.array(chunk_ids, dtype=np.int64)) # type: ignore

    return index
        
    


def search_index(index: faiss.IndexFlatIP, query_vector: np.ndarray, k: int = 3):
    """
    A function that searches a FAISS index for the top-k most similar vectors to a query embedding.
    """

    q = np.asarray(query_vector, dtype=np.float32)

    if q.ndim == 1:
        q = q[None, :]
    faiss.normalize_L2(q)
    distances, ids = index.search(q, k) # type: ignore
    return distances, ids