import faiss
import numpy as np




def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    A function that builds a FAISS vector index from a set of embeddings.
    """    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(embeddings)
    index.add(embeddings) # type: ignore

    return index
        
    


def search_index(index: faiss.IndexFlatIP, query_vector: np.ndarray, k: int = 3):
    """
    A function that searches a FAISS index for the top-k most similar vectors to a query embedding.
    """
    faiss.normalize_L2(query_vector)
    distances, ids = index.search(query_vector, k) # type: ignore
    return distances, ids