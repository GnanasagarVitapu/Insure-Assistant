import config
from vectorstore import VectorStore

class Retriever:
    def __init__(self, store: VectorStore, embedding_model=config.embedding_model):
        self.store = store
        self.embedding_model = embedding_model

    def retrieve(self, query: str, top_k:int=5, source_type_filter:str=None):
        query_embedding = config.emb_client.embeddings.create(
            model=self.embedding_model,
            input=query
        ).data[0].embedding

        results = self.store.search(
            query_embedding,
            top_k=top_k,
            source_type_filter=source_type_filter
        )

        return results