from pathlib import Path

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