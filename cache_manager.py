from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class QueryCache:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.queries = []     # Stores enriched queries
        self.entries = []     # Stores dicts with SQL + results
        self.index = None

    def _rebuild_index(self):
        """Rebuild FAISS index whenever a new query is added."""
        if not self.queries:
            self.index = None
            return
        embeddings = self.model.encode(self.queries).astype("float32")
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def add(self, enriched_question, sql, result_tuple):
        """
        Add a new query to cache.
        result_tuple = (json_result, ascii_result)
        """
        print(f"[CACHE ADD] Storing query: {enriched_question[:60]}...")
        self.queries.append(enriched_question)
        self.entries.append({
            "enriched": enriched_question,
            "sql": sql,
            "json_result": result_tuple[0],   # structured JSON
            "ascii_result": result_tuple[1]   # pretty table string
        })
        self._rebuild_index()

    def search(self, enriched_question, threshold=0.80):
        """
        Search for a similar query in cache.
        Returns (sql, (json_result, ascii_result)) if found.
        """
        if not self.index:
            print("[CACHE MISS] Cache empty")
            return None

        print(f"[CACHE SEARCH] Looking for: {enriched_question[:60]}...")
        q_emb = self.model.encode([enriched_question]).astype("float32")
        D, I = self.index.search(q_emb, 1)
        score = 1 / (1 + D[0][0])

        if score >= threshold:
            print(f"[CACHE HIT] score={score:.2f}")
            match = self.entries[I[0][0]]
            return match["sql"], (match["json_result"], match["ascii_result"])

        print(f"[CACHE MISS] score={score:.2f}")
        return None
