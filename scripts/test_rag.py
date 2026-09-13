from app.rag.faiss_store import retrieve_faiss_context


query = "I want hiking in Iceland during October"


context = retrieve_faiss_context(
    query,
    top_k=3
)


print(context)