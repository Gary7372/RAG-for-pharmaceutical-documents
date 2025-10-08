 This RAG system efficiently processes a large number of PDFs by separating text and image-based
 table data into two FAISS vectorstores to avoid retrieval conflicts and ensure accuracy. Text is
 extracted using PyMuPDF, with each page treated as a chunk for context preservation and embedding
 efficiency, while image-based tables are converted into images, OCR-processed via Adobe PDF
 Services, and stored as CSVs. During retrieval, raw text chunks or structured CSV data are passed to
 different LLMs—Mistral for table interpretation and Claude for final answer generation—ensuring
 tailored, natural language responses. The system uses Amazon Titan for embeddings, stores data in
 SQLite3, and is orchestrated using chatbedrock with controlled temperature settings. 
