import json
import numpy as np
import config
from sparse_scoring import keyword_boost, TfidfScorer, BM25Scorer

with open("embedded_chunks.json", "r", encoding="utf-8") as f:
    embedded_chunks = json.load(f)

corpus_texts = [c["chunk_text"] for c in embedded_chunks]
tfidf = TfidfScorer(corpus_texts)
bm25 = BM25Scorer(corpus_texts)

def cosine_similarity_manual(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def compare_retrieval_methods(query: str, top_n :int=5):
    query_embedding = config.emb_client.embeddings.create(
        model=config.embedding_model,
        input=query
    ).data[0].embedding

    tfidf_scores = tfidf.score(query)
    bm25_scores = bm25.score(query)

    results = []
    for i, chunk in enumerate(embedded_chunks):
        dense = cosine_similarity_manual(query_embedding, chunk["embedding"])
        binary_kw = keyword_boost(query, chunk["chunk_text"])
        results.append({
            "document_name": chunk["document_name"],
            "section": chunk["section"],
            "chunk_text": chunk["chunk_text"],
            "dense": dense,
            "binary_keyword": binary_kw,
            "tfidf": tfidf_scores[i],
            "bm25": bm25_scores[i]
        })

    results.sort(key=lambda x: x["dense"], reverse=True)
    print(f"\n=== Query: {query} ===")
    for r in results[:top_n]:
        print(f"{r['document_name']:20} | {r['section']:20} | {r['chunk_text'][:50]} |"
              f"dense={r['dense']:.3f} | kw={r['binary_keyword']:.3f} | "
              f"tfidf={r['tfidf']:.3f} | bm25={r['bm25']:.2f}")

compare_retrieval_methods("What is Alex Chen's current salary?")
compare_retrieval_methods("can you tell me about contract HL-2025-0124")
compare_retrieval_methods("is there any one in the company who completed machine learning training?")
