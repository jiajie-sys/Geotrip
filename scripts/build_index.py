from app.rag.faiss_store import (
    build_faiss_index,
    save_faiss_index
)


def main():
    print("正在构建 GeoTrip FAISS 索引...")

    index, chunks = build_faiss_index()

    save_faiss_index(
        index=index,
        chunks=chunks
    )

    print(f"索引构建完成，共写入 {index.ntotal} 个向量。")


if __name__ == "__main__":
    main()