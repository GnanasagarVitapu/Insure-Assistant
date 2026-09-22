from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

def keyword_boost(query, chunk_text) -> float:
    query_terms = query.lower().split()
    chunk_lower = chunk_text.lower()

    matches = sum(1 for term in query_terms if term in chunk_lower)
    return matches / len(query_terms) if query_terms else 0.0

class TfidfScorer:
    def __init__(self, corpus_texts: list):
        self.vectorizer = TfidfVectorizer(lowercase=True)
        self.doc_vectors = self.vectorizer.fit_transform(corpus_texts)

    def score(self, query:str):
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]
        return similarities

class BM25Scorer:
    def __init__(self, corpus_texts: list):
        tokenized_corpus = [doc.lower().split() for doc in corpus_texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def score(self, query:str):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        return scores