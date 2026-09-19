import json
from pathlib import Path
from vectorstore_chroma_db import VectorStore

def load_documents(data_dir="knowledge-base"):
    documents=[]
    base_path = Path(data_dir)

    for source_type_dir in base_path.iterdir():
        if not source_type_dir.is_dir():
            continue
        source_type = source_type_dir.name
        for file_path in source_type_dir.glob("*.md"):
            text = file_path.read_text(encoding="utf-8")
            documents.append({
                "source_type": source_type,
                "document_name": file_path.stem,
                "raw_text": text
            })

    return documents

#loaded_documents = load_documents()
#with open("loaded_documents.json", "w", encoding="utf-8") as f:
#    json.dump(loaded_documents, f, ensure_ascii=False, indent=4)

def load_data_from_json(json_path="embedded_chunks.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    store = VectorStore()
    store.load_chunks(documents)
    return f"Loaded {store.collection.count()} documents into chromadb"

print(load_data_from_json())