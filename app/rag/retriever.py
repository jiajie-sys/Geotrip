from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

def get_embedding(text: str):
    embedding = model.encode(text)
    return embedding

def cosine_similarity(vector_a, vector_b):
    dot_product = vector_a @ vector_b

    norm_a = (vector_a @ vector_a) ** 0.5
    norm_b = (vector_b @ vector_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
def retrieve(query: str, chunks: list[str], top_k: int = 2):
    query_embedding = get_embedding(query)

    results = []

    for chunk in chunks:
        chunk_embedding = get_embedding(chunk)

        score = cosine_similarity(
            query_embedding,
            chunk_embedding
        )

        results.append({
            "text": chunk,
            "score": float(score)
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]
def retrieve_context(query: str, top_k: int = 2):
    from app.rag.knowledge_loader import (
        load_knowledge,
        split_markdown_sections
    )

    content = load_knowledge()
    chunks = split_markdown_sections(content)

    results = retrieve(
        query=query,
        chunks=chunks,
        top_k=top_k
    )

    context = "\n\n".join(
        result["text"] for result in results
    )

    return context