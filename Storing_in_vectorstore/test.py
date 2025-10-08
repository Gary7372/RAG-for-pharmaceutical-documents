import os
import datetime
import shutil
import pandas as pd
import fitz  # PyMuPDF
from typing import List
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import  BedrockEmbeddings

# === ENVIRONMENT SETUP ===
load_dotenv()
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

def debug_log(msg: str):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🔍 {msg}")

# === 1. Process PDF files ===
def process_pdf_files(pdf_folder: str) -> List[Document]:
    debug_log(f"📂 Processing PDF files in: {pdf_folder}")
    documents = []

    for file_name in os.listdir(pdf_folder):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, file_name)
            try:
                pdf_doc = fitz.open(pdf_path)
                num_pages = len(pdf_doc)
                debug_log(f"📄 {file_name} has {num_pages} pages")

                for page_num in range(num_pages):
                    page_text = pdf_doc[page_num].get_text().strip()
                    if not page_text:
                        continue

                    page_text += f"\n\nthis is a text chunk - {file_name}"

                    documents.append(
                        Document(
                            page_content=page_text,
                            metadata={
                                "source": pdf_path,
                                "file_name": file_name,
                                "method": "PDF single page chunk",
                                "chunk_id": page_num,
                                "pages": str(page_num + 1),
                            }
                        )
                    )

                debug_log(f"📦 Created {num_pages} chunks from PDF: {file_name}")

            except Exception as e:
                debug_log(f"⚠️ Failed to process PDF {file_name}: {e}")

    return documents
# === 2. Process CSV files ===
from transformers import AutoTokenizer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
MAX_TOKENS = 500


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, truncation=False))


def split_csv_by_tokens(csv_text: str, max_tokens: int) -> List[str]:
    lines = csv_text.strip().splitlines()
    header = lines[0]
    rows = lines[1:]

    chunks = []
    current_chunk = [header]
    current_token_count = count_tokens(header)

    for row in rows:
        row_token_count = count_tokens(row)
        if current_token_count + row_token_count > max_tokens:
            chunk_text = "\n".join(current_chunk) + "\n\nthis is a csv"
            chunks.append(chunk_text)
            current_chunk = [header, row]
            current_token_count = count_tokens(header) + row_token_count
        else:
            current_chunk.append(row)
            current_token_count += row_token_count

    if len(current_chunk) > 1:
        chunk_text = "\n".join(current_chunk) + "\n\nthis is a csv"
        chunks.append(chunk_text)

    return chunks


def process_csv_files(csv_folder: str) -> List[Document]:
    debug_log(f"📂 Processing CSV files in: {csv_folder}")
    docs = []

    for csv_file in os.listdir(csv_folder):
        if csv_file.lower().endswith(".csv"):
            csv_path = os.path.join(csv_folder, csv_file)
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                content_with_note = content + "\n\nthis is a csv"

                token_count = count_tokens(content_with_note)
                debug_log(f"📏 Token count for {csv_file}: {token_count}")

                if token_count > MAX_TOKENS:
                    debug_log(f"🔪 Splitting CSV: {csv_file} (> {MAX_TOKENS} tokens)")
                    chunks = split_csv_by_tokens(content, MAX_TOKENS)
                    for i, chunk in enumerate(chunks):
                        docs.append(
                            Document(
                                page_content=chunk,
                                metadata={
                                    "source": csv_path,
                                    "file_name": csv_file,
                                    "method": "CSV chunk",
                                    "chunk_id": i
                                }
                            )
                        )
                else:
                    docs.append(
                        Document(
                            page_content=content_with_note,
                            metadata={
                                "source": csv_path,
                                "file_name": csv_file,
                                "method": "CSV file",
                                "chunk_id": 0
                            }
                        )
                    )
                debug_log(f"📊 Processed CSV: {csv_file}")
            except Exception as e:
                debug_log(f"⚠️ Failed to read CSV {csv_file}: {e}")
    return docs



# === 3. Embedding Generator ===
class EmbeddingGenerator:
    def __init__(self, embedder, batch_size=64, max_workers=4):
        self.embedder = embedder
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.lock = Lock()
        self.embeddings = []
        self.processed = 0

    def _process_batch(self, batch):
        texts = [doc.page_content for doc in batch]
        batch_embeddings = self.embedder.embed_documents(texts)
        with self.lock:
            self.embeddings.extend(batch_embeddings)
            self.processed += len(batch)
            debug_log(f"✅ Processed batch ({self.processed} embeddings done)")

    def generate_embeddings(self, documents):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]
                futures.append(executor.submit(self._process_batch, batch))
            for future in futures:
                future.result()
        return self.embeddings

# === 4. MAIN ===
def main():
    pdf_folder = "Data"             # 📂 Folder containing PDF files
    csv_folder = "csv_files"             # 📂 Folder containing CSV files
    faiss_dir_text = "faiss_db_text"     # 📦 Vector DB for PDFs
    faiss_dir_csv = "faiss_db_csv"       # 📦 Vector DB for CSVs

    embedder = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",  # Titan model
    region_name="eu-west-1",                  # Update region if needed
)

    # === PDF Processing ===
    pdf_docs = []
    if os.path.exists(pdf_folder):
        pdf_docs = process_pdf_files(pdf_folder)
    else:
        debug_log(f"⚠️ PDF folder not found: {pdf_folder}")

    debug_log(f"📘 Total PDF chunks to embed: {len(pdf_docs)}")
    if pdf_docs:
        pdf_generator = EmbeddingGenerator(embedder)
        pdf_embeddings = pdf_generator.generate_embeddings(pdf_docs)

        debug_log("💾 Saving PDF FAISS index...")
        texts = [doc.page_content for doc in pdf_docs]
        metadatas = [doc.metadata for doc in pdf_docs]
        vectorstore = FAISS.from_embeddings(
            text_embeddings=list(zip(texts, pdf_embeddings)),
            embedding=embedder,
            metadatas=metadatas
        )
        if os.path.exists(faiss_dir_text):
            shutil.rmtree(faiss_dir_text)
        vectorstore.save_local(faiss_dir_text)
        debug_log(f"✅ FAISS index for PDFs saved at '{faiss_dir_text}'")

    # === CSV Processing ===
    csv_docs = []
    if os.path.exists(csv_folder):
        csv_docs = process_csv_files(csv_folder)
    else:
        debug_log(f"⚠️ CSV folder not found: {csv_folder}")

        debug_log(f"📈 Total CSV documents to embed: {len(csv_docs)}")
    if csv_docs:
        csv_generator = EmbeddingGenerator(embedder)
        csv_embeddings = csv_generator.generate_embeddings(csv_docs)

        debug_log("💾 Saving CSV FAISS index...")
        texts = [doc.page_content for doc in csv_docs]
        metadatas = [doc.metadata for doc in csv_docs]
        vectorstore = FAISS.from_embeddings(
            text_embeddings=list(zip(texts, csv_embeddings)),
            embedding=embedder,
            metadatas=metadatas
        )
        if os.path.exists(faiss_dir_csv):
            shutil.rmtree(faiss_dir_csv)
        vectorstore.save_local(faiss_dir_csv)
        debug_log(f"✅ FAISS index for CSVs saved at '{faiss_dir_csv}'")

        # === Final Check ===
    #if not pdf_docs and not csv_docs:
        debug_log("❌ No data processed. Nothing saved.")


if __name__ == "__main__":
    main()


