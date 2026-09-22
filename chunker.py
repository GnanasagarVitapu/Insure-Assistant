import re
import loader

def chunk_by_headers(raw_text: str, document_name: str, source_type: str):
    title_match = re.match(r"^#\s+(.+)", raw_text.strip())
    h1_matches = re.findall(r"^#\s+(.+)", raw_text.strip(), re.MULTILINE)
    title = h1_matches[-1] if h1_matches else document_name

    h2_sections = re.split(r"\n(?=##\s)", raw_text)
    chunks = []

    for section in h2_sections:
        section = section.strip()
        if not section:
            continue

        h2_match = re.match(r"##\s+(.+)", section)
        if h2_match:
            section_name = h2_match.group(1)
            body = re.sub(r"^##\s+.+\n", "", section, count=1).strip()
        else:
            section_name = "Overview"
            lines = section.split("\n")
            while lines:
                stripped = lines[0].strip()
                if stripped == "" or (stripped.startswith("#") and not stripped.startswith("##")):
                    lines.pop(0)
                else:
                    break
            body = "\n".join(lines).strip()

        if not body:
            continue  # nothing left after stripping header — skip empty chunk

        h3_subsections = re.split(r"\n(?=###\s)", body)
        if len(h3_subsections) > 1:
            for sub in h3_subsections:
                sub = sub.strip()
                if not sub:
                    continue
                h3_match = re.match(r"###\s+(.+)", sub)
                if h3_match:
                    sub_section_name = h3_match.group(1)
                    sub_body = re.sub(r"^###\s+.+\n", "", sub, count=1).strip()
                    chunks.append({
                        "source_type": source_type,
                        "document_name": document_name,
                        "section": f"{section_name}",
                        "subsection": f"{sub_section_name}",
                        "chunk_text": f"{title} — {section_name} — {sub_section_name}\n\n{sub_body}"
                    })
                else:
                    chunks.append({
                        "source_type": source_type,
                        "document_name": document_name,
                        "section": f"{section_name}",
                        "subsection": None,
                        "chunk_text": f"{title} — {section_name}\n\n{sub}"
                    })
        else:
            chunks.append({
                "source_type": source_type,
                "document_name": document_name,
                "section": section_name,
                "subsection": None,
                "chunk_text": f"{title} — {section_name}\n\n{body}"
            })

    return chunks

docs = loader.load_documents()
chunks = []
for doc in docs:
    chunks.extend(chunk_by_headers(doc["raw_text"], doc["document_name"], doc["source_type"]))

short_chunks = [c for c in chunks if len(c["chunk_text"]) < 60]
for c in short_chunks:
    print(c["document_name"], "|", c["section"], "->", repr(c["chunk_text"]))

print(f"\nTotal chunks in corpus: {len(chunks)}")
print(f"Short/suspicious chunks: {len(short_chunks)}")