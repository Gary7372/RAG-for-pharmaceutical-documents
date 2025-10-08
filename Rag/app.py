import streamlit as st
from graph_builder import build_graph
from generator import generate_answer
from langchain.schema import Document
from dotenv import load_dotenv
from db import init_db, save_conversation

load_dotenv()
init_db()

st.set_page_config(page_title="💊 Pharma QA Assistant", layout="wide")
st.title("💊 Pharma QA Assistant")

# Step 1: Let user select retrieval source
retrieval_label = st.radio(
    "Select data source:",
    options=["Text Documents including intext tables", "Tables embedded in images"],
    index=0
)

# Step 2: Normalize to expected values for retriever
retrieval_source = "text" if retrieval_label == "Text Documents including intext tables" else "csv"

# Step 3: Query box
query = st.text_input("Enter your pharmaceutical question:")

if query:
    with st.spinner("Retrieving and analyzing documents..."):
        from retriever import get_retriever
        retriever = get_retriever(source=retrieval_source)

        app = build_graph(retriever)
        result = app.invoke({"query": query})
        documents: list[Document] = result.get("documents", [])

        if not documents:
            st.warning("No documents retrieved. Try a different query.")
        else:
            answer = result.get("answer", "")
            instruction_prompt = generate_answer(query, documents)[1]

            save_conversation(query, answer, instruction_prompt)

            st.markdown("## ✅ Answer")
            st.write(answer)

            st.markdown("## 📋 Prompt used for LLM")
            with st.expander("Show prompt"):
                st.code(instruction_prompt)

            st.markdown("## 📄 Retrieved Document Chunks")
            for i, doc in enumerate(documents, 1):
                is_csv = doc.metadata.get("csv_processed", False)
                label = f"Chunk {i} — {'📊 CSV Summary' if is_csv else '📝 Text'}"
                with st.expander(label):
                    st.markdown(doc.page_content)
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page", "?")
                    st.caption(f"📎 Source: {source} | Page: {page}")



