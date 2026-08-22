import re
import loader

def chunk_by_headers(raw_text: str, document_name: str, source_type: str):
    title_match = re.match(r"^#\s+(.+)", raw_text.strip())
    title = title_match.group(1) if title_match else document_name

    sections = re.split(r"\n(?=##\s)", raw_text)

    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        header_match = re.match(r"##\s+(.+)", section)
        if header_match:
            section_name = header_match.group(1)
            body = re.sub(r"^##\s+.+\n", "", section, count=1).strip()
        else:
            # No H2 header in this section — likely the H1 title + body with no ## splits
            section_name = "Overview"
            body = re.sub(r"^#\s+.+\n", "", section, count=1).strip()

        if not body:
            continue  # nothing left after stripping header — skip empty chunk

        chunks.append({
            "source_type": source_type,
            "document_name": document_name,
            "section": section_name,
            "chunk_text": f"{title} — {section_name}\n\n{body}"
        })

    return chunks

docs = loader.load_documents()
contract_doc = next(d for d in docs if d["source_type"] == "company")
chunks = chunk_by_headers(contract_doc["raw_text"], contract_doc["document_name"], contract_doc["source_type"])
for c in chunks:
    print(f"--- {c['section']} ---")
    print(c["chunk_text"][:150])
    print()