# Insurellm RAG Assistant

A Retrieval-Augmented Generation (RAG) system built over a dummy insurance-company knowledge base, built as a hands-on learning project to go deep on RAG fundamentals — chunking, embeddings, retrieval, and conversational grounding — rather than relying on a framework.

Knowledge base credit: dummy data adapted from a course by Ed Donner — thanks to him for the dataset.

---

## 1. Knowledge Base Structure

The data is organized into four folders, cleanly segregated by domain:

| Folder | Contents |
|---|---|
| `company/` | About, careers, culture, overview — general company info |
| `contracts/` | 32 client contracts across all product lines |
| `employees/` | 32 HR records |
| `products/` | 8 product summaries |

**Observations from inspecting the raw files:**
- All files are Markdown, with a consistent header hierarchy: an **H1** title, then **H2** sections (e.g. Terms, Renewal, Features, Support for contracts; Summary, Career Progression, Compensation History for employees).
- Some H2 sections contain further **H3** subsections — most notably product docs, where `## Features` breaks into 8–9 individual `### <Feature Name>` entries.
- Not every document has H2 headers — `about.md`, for example, is a single H1 with body text and no further sectioning.

This consistency (and the deliberate exceptions) directly shaped the chunking strategy below.

---

## 2. Chunking Strategy

**Decision: chunk by markdown header hierarchy, not fixed token size.**

Fixed-size chunking risks splitting a document mid-sentence or mid-section (e.g. cutting a contract's Payment Terms paragraph in half), which actively degrades retrieval and generation quality even when the answer exists in the source. Since every document already has clean semantic boundaries via its headers, splitting on those boundaries keeps every chunk whole and self-contained.

**Rule:** split on H2 headers. If an H2 section itself contains H3 subsections, split further — one chunk per H3. If a document has no H2 at all, the entire body becomes a single "Overview" chunk.

**Final chunk schema:**
```json
{
  "source_type": "contracts | employees | products | company",
  "document_name": "filename stem, e.g. Contract_with_BrightWay_Solutions_for_Markellm",
  "section": "H2 section name, e.g. 'Terms' or 'Features'",
  "subsection": "H3 name if present, else null",
  "chunk_text": "Title — Section — Subsection\n\n<body text>",
  "embedding": "vector, added in a separate embedding pass"
}
```

Chunks are generated first as plain JSON (no embeddings), then embedded in a second pass — keeping chunking and embedding as independent, separately-testable steps.

---

## 3. Embedding & Storage

- Model: `text-embedding-3-small` (OpenAI), called in batches rather than one chunk at a time, to reduce API round-trips.
- ~490 chunks total across the full corpus — small enough that a **plain in-memory list + cosine similarity** was used instead of a real vector database. This was a deliberate choice to understand the retrieval mechanism directly before reaching for a library (Chroma/FAISS/Pinecone) that would hide it.
- Each chunk's embedding + metadata is cached to a local JSON file after the first embedding run, so development iteration doesn't re-spend API calls re-embedding unchanged data.

**Rule enforced throughout:** the same embedding model is used for every chunk and every query. Embeddings from different models are not comparable — even the same text embedded by two different models produces vectors that can't be meaningfully compared to each other. Chat generation, separately, has no such constraint — the chat model consuming retrieved context can be entirely different from the embedding model.

---

## 4. Retrieval → Generation Flow

1. User asks a question.
2. Question is embedded with the same model used for the corpus.
3. Cosine similarity search returns the top-k most relevant chunks.
4. Retrieved chunks are formatted with source labels and inserted into the prompt as context, ahead of the user's question.
5. The chat model is instructed to answer **only** from the provided context, and to say so explicitly if the context doesn't contain enough information — rather than falling back on its own general knowledge.

---

## 5. Issues Found, and How They Were Fixed

### 5.1 Missing content in documents with no H2 headers
**Symptom:** `about.md` (H1 + body, no `##` at all) produced zero chunks.
**Cause:** the chunker's "skip if this is just the title line" filter matched the *entire* document (since without any H2 split, the whole file starts with `# `), silently discarding all body content.
**Fix:** explicitly branch on whether an H2 header is present in a given section. If not, treat it as a whole-document "Overview" chunk and strip only the H1 line, not the whole blob.

### 5.2 Duplicated header text inside chunk bodies
**Symptom:** each chunk repeated its section name twice — once in the generated title prefix, once because the raw `##`/`###` line was still embedded in the body text.
**Fix:** strip the header line from the body before building the final `chunk_text`, since the section/subsection name is already carried in structured metadata and the title prefix.

### 5.3 Coarse chunking on multi-feature sections
**Symptom:** product docs' entire `## Features` section (8–9 distinct features) was stored as a single chunk, diluting embedding relevance for feature-specific queries.
**Fix:** recursive splitting — detect H3 headers inside an H2 section and split further, one chunk per H3, falling back to the original H2-level chunk when no H3s exist (contracts, employee records).

### 5.4 Entity ambiguity between similarly-named records
**Symptom:** querying "What is Alex Chen's current salary?" returned a mix of *Alex Chen* and *Alex Thomson* chunks, with the correct chunk (Compensation History) not even in the top 3.
**Root cause, in two parts:**
- Every employee file has **two H1 headers** (`# HR Record` followed by `# <Employee Name>`). The chunker's title extraction grabbed the first H1 ("HR Record") for every employee, meaning all 32 employees' chunks shared an identical, uninformative title prefix — actively making different people's records look more similar to each other in embedding space.
- More generally: semantic embedding search matches on *meaning/topic*, not exact entity identity. Two people with similar role/compensation language can outscore each other on a shared first name.
**Fixes applied:**
- Extract the *last* H1 in a document (not the first), correctly capturing the person's actual name as the title.
- Documented as a known limitation: exact entity names (people, contract IDs) are still best resolved via metadata filtering rather than embedding similarity alone — a planned next step (see §7).

### 5.5 RAG context silently accumulating in conversation memory
**Symptom:** token usage grew rapidly turn over turn in a multi-turn session; no functional error, just runaway cost/context growth.
**Cause:** the per-turn context-augmented prompt (retrieved chunks + question, potentially hundreds of tokens) was being stored via `add_user_message()` as if it were the user's actual message — meaning every past turn's *entire retrieved context* was being resent, unchanged, on every subsequent call, forever.
**Fix:** clear separation of concerns — retrieved context is **call-scoped**, built fresh each turn and used only for that one API call. Conversation memory stores only the user's original raw question and the model's final answer, never the retrieved context blob.

### 5.6 Follow-up questions failing retrieval entirely
**Symptom:** after "What is Alex Chen's current salary?" → "what about his job title?", the second query retrieved unrelated chunks (random employees), because "his job title" alone carries almost no resolvable signal for embedding search.
**Fix:** query rewriting. Before retrieval, a separate lightweight LLM call rewrites the raw follow-up into a self-contained query using conversation history (resolving pronouns to the actual named entity), e.g. "what about his job title?" → "What is Alex Chen's job title?". The rewritten query is used only for retrieval; the user's original phrasing is preserved in conversation history and in the final answer-generation prompt.

---

## 6. Architecture

```
insurellm-rag-assistant/
├── data/
│   ├── company/
│   ├── contracts/
│   ├── employees/
│   └── products/
├── config.py          # env vars, OpenAI client
├── loader.py          # reads files from data/, tags with source_type
├── chunker.py          # header-hierarchy-aware chunking
├── embedder.py         # batch embedding calls
├── vectorstore.py      # in-memory store + cosine similarity search
├── retriever.py         # query -> embedding -> search, clean interface
├── memory.py            # conversation history, sliding window trim
├── rag_chat.py           # retrieval + generation + query rewriting
└── main.py               # CLI loop
```

---

## 7. Known Limitations / Next Steps

- **No hybrid search yet.** Dense (embedding) similarity alone is weak on exact-string identity (names, contract IDs, numbers). A keyword/BM25-style signal blended with semantic similarity would give more robust disambiguation than the title fix alone provides.
- **No metadata-based exact filtering yet.** When a query unambiguously names an entity (a specific employee, contract, or product), the system should be able to hard-filter to that document rather than relying on similarity ranking alone.
- **No RAG evaluation harness yet.** No systematic check (e.g. RAGAS-style faithfulness/relevance/context-recall metrics) exists yet to catch retrieval or grounding regressions as the system evolves.
- **Citation fidelity is not verified.** The chat model is trusted to relay source labels back accurately in its answers; this hasn't been validated against cases where it might paraphrase or misattribute a citation.
- **Single-domain corpus assumption.** Chunking assumes consistent header structure across all documents in a category; this held true for the full dataset here but isn't validated as a general-purpose chunker for arbitrary markdown.
