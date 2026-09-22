import config
from loader import load_documents
from chunker import chunk_by_headers
import json

def embed_chunks(chunks: list, batch_size = 20):
    embeded_chunks = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        #print(f"batch: {batch}")
        texts = [c["chunk_text"] for c in batch]
        #print(f"texts : {texts}")

        response = config.emb_client.embeddings.create(
            model=config.embedding_model,
            input=texts
        )

        for chunk, embedding_data in zip(batch, response.data):
            chunk_with_embedding = {**chunk, "embedding": embedding_data.embedding}
            #print(f"chunk_with_embedding: {chunk_with_embedding}")
            embeded_chunks.append(chunk_with_embedding)

    return embeded_chunks

all_docs = load_documents()
all_chunks = []
for doc in all_docs:
    all_chunks.extend(chunk_by_headers(doc["raw_text"], doc["document_name"], doc["source_type"]))

embedded = embed_chunks(all_chunks)

with open("embedded_chunks.json", "w") as f:
    json.dump(embedded, f)