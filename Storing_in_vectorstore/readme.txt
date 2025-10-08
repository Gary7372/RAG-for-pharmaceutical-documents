# PDF and CSV Vectorstore Builder with LangChain and Bedrock Embeddings

## Overview

This project processes PDF and CSV files, splits their content into manageable chunks, generates embeddings using Amazon Bedrock's Titan embedding model, and stores them in FAISS vector databases separately for text (PDFs) and tables (CSVs).

---

## Features

- Extracts text from PDF files page by page.
- Processes CSV files and splits large CSVs by token count.
- Generates embeddings in batches with multithreading.
- Saves FAISS vectorstore indexes locally for PDFs and CSVs.
- Uses Bedrock's Titan model for embedding generation.
- Logs detailed debug info during processing.

---

## Setup

### Prerequisites

- Python 3.8+
- AWS Bedrock access configured with credentials.
- `.env` file configured with necessary AWS keys (if applicable).
- pdfs and csv files
### Installation

```bash
pip install -r requirements.txt



