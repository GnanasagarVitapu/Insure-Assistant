import json
import numpy as np
import config

class VectorStore:
    def __init__(self):
        self.chunks = []

    def load(self, path="embedded_chunks.json"):
        with open(path) as f:
            self.chunks = json.load(f)

    def search(self, query_embedding, top_k=5, source_type_filter=None):
        candidates = self.chunks
        if source_type_filter:
            candidates = [c for c in candidates if c["source_type"] == source_type_filter]

        scored = []
        for chunk in candidates:
            similarity = self._cosine_similarity(query_embedding, chunk["embedding"])
            scored.append((similarity, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _cosine_similarity(a, b):
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))