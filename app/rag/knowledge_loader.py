from pathlib import Path

KNOWLEDGE_DIR = Path("data/knowledge")


def load_knowledge():
    contents = []

    for file_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        contents.append(content)

    return "\n\n".join(contents)


def split_knowledge(content: str):
    chunks = content.split("\n\n")

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def split_by_size(
    content: str,
    chunk_size: int = 100,
    overlap: int = 20
):
    chunks = []

    step = chunk_size - overlap

    for start in range(0, len(content), step):
        end = start + chunk_size
        chunk = content[start:end]
        chunks.append(chunk)

    return chunks


def split_markdown_sections(content: str):
    sections = []
    current_section = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current_section:
                sections.append("\n".join(current_section).strip())
                current_section = []

        if line.startswith("# ") and not line.startswith("## "):
            continue

        current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section).strip())

    return [
        section
        for section in sections
        if section
    ]