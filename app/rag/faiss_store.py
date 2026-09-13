from pathlib import Path
import json

import faiss
import numpy as np

from app.rag.knowledge_loader import (
    load_knowledge,
    split_markdown_sections
)

from app.rag.retriever import get_embedding


INDEX_PATH = Path("data/faiss.index")
CHUNKS_PATH = Path("data/faiss_chunks.json")


def build_faiss_index():
    content = load_knowledge()

    chunks = split_markdown_sections(
        content
    )

    embeddings = [
        get_embedding(chunk)
        for chunk in chunks
    ]

    vectors = np.array(
        embeddings,
        dtype="float32"
    )

    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    faiss.normalize_L2(
        vectors
    )

    index.add(
        vectors
    )

    return index, chunks



def search_faiss(
    query: str,
    index,
    chunks,
    top_k: int = 2
):

    query_vector = get_embedding(
        query
    )

    query_vector = np.array(
        [query_vector],
        dtype="float32"
    )

    faiss.normalize_L2(
        query_vector
    )


    scores, indices = index.search(
        query_vector,
        top_k
    )


    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < len(chunks):

            results.append(
                {
                    "text": chunks[idx],
                    "score": float(score)
                }
            )


    return results



def save_faiss_index(
    index,
    chunks
):

    INDEX_PATH.parent.mkdir(
        exist_ok=True
    )


    faiss.write_index(
        index,
        str(INDEX_PATH)
    )


    CHUNKS_PATH.write_text(
        json.dumps(
            chunks,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )



def load_faiss_index():

    index = faiss.read_index(
        str(INDEX_PATH)
    )


    chunks = json.loads(
        CHUNKS_PATH.read_text(
            encoding="utf-8"
        )
    )


    return index, chunks



def retrieve_faiss_context(
    query: str,
    top_k: int = 2
):

    index, chunks = load_faiss_index()


    results = search_faiss(
        query=query,
        index=index,
        chunks=chunks,
        top_k=top_k
    )


    context = "\n\n".join(
        result["text"]
        for result in results
    )


    return context