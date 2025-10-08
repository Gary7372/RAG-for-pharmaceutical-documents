from langchain.vectorstores import FAISS
from langchain.embeddings import BedrockEmbeddings

def get_retriever(source: str = "text"):

    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        region_name="eu-west-1",
    )

    if source == "csv":
        db_path = "faiss_db_csv"
    else:
        db_path = "faiss_db_text"

    vectorstore = FAISS.load_local(
        db_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    def retriever(query: str, k: int = 10):
        if source == "csv":
            return vectorstore.similarity_search(query=query, k=7)
        else:
            return vectorstore.similarity_search(query=query, k=k)

    return retriever