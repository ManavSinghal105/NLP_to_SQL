from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SchemaRetriever:
    """Embeds schema info, retrieves relevant parts for queries."""

    def __init__(self, schema_info, model_name="all-MiniLM-L6-v2"):
        self.schema_info = schema_info
        self.model = SentenceTransformer(model_name)

        embeddings = self.model.encode(schema_info).astype("float32")
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, query, top_k=2):
        query_emb = self.model.encode([query]).astype("float32")
        D, I = self.index.search(query_emb, top_k)
        return [self.schema_info[i] for i in I[0]]
