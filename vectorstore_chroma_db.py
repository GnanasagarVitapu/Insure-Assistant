import chromadb

class VectorStore:
    def __init__(self, persist_dir="./chroma_db", collection_name="insurelmm"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    def load_chunks(self, chunks: list):
        ids = [f"{c["document_name"]}_{c["section"]}_{c.get("subsection", "none")}_{i}" for i, c in enumerate(chunks)]
        embeddings = [c["embedding"] for c in chunks]
        documents = [c["chunk_text"] for c in chunks]
        metadatas = [{
            "source_type": c["source_type"],
            "document_name": c["document_name"],
            "section": c["section"],
            "subsection": c.get("subsection") or ""
        } for c in chunks]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_embedding, top_k=5, source_type_filter=None):

        where_clause = {"source_type": source_type_filter} if source_type_filter else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )

        output = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance  # Convert distance to similarity
            chunk = {
                "chunk_text": results["documents"][0][i],
                **results["metadatas"][0][i],
            }
            output.append((similarity, chunk))
        return output
