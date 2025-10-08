💊 Pharma QA Assistant – RAG-Based Chatbot
A Retrieval-Augmented Generation (RAG) chatbot designed to answer pharmaceutical or weather-related questions by retrieving and reasoning over text and table data, including tables embedded in images.

🔧 Usage Guidelines
This chatbot supports two types of document input for querying:

Text Documents: Includes paragraphs and inline tables from PDF documents.

Image-based Tables: Tables embedded as images within PDFs.

📝 Input Instructions
Use complete and clear sentences when querying.

Specify exact column and row names when referencing tables.

Numeric accuracy may vary when retrieving from table images (due to OCR).

Select the correct data source ("Text" or "Table") from the Streamlit UI.

Ensure all API keys (especially for ChatBedrock) are set before launching.

💻 Local Setup
2. Install Dependencies
pip install -r requirements.txt
3. Run the App
python -m streamlit run app.py
A local SQLite3 database will be created to store your conversation history.

🐳 Docker Instructions
Load Prebuilt Docker Image
If you received a .tar Docker image file:


docker load -i pharma-qa.tar
This loads the image with the tag pharma-qa.

Run the App in Docker
docker run -p 8501:8501 pharma-qa
Access the App
Once running, open your browser and go to
http://localhost:8501
Optional: Remove Docker Image
To delete the image:

docker rmi pharma-qa
🧠 Algorithm Overview
The system uses two separate FAISS vectorstores:

Source	Use Case	Details
Text Vectorstore	Paragraphs, in-line tables	Pages are chunked individually to preserve context and reduce token load.
CSV Vectorstore	Tables from image-based PDFs	Tables extracted via OCR and stored as CSVs for structured querying.

Retrieval Logic
Text selected → Raw text chunks are passed directly to the LLM.

Table selected:

CSV tables are passed to an LLM (Mistral) for interpretation.

Output is converted into natural language.

Final answer is generated using Claude.

🗃️ Data Storage & Extraction Workflow
Text Extraction
Uses PyMuPDF.

Each page is a chunk (context preservation + embedding efficiency).

Text-based tables are retained for LLM interpretation.

Image-Based Table Extraction
Pages with image-based tables are converted into images (full-page).

Grouped into 25-page PDFs due to Adobe API limits.

OCR is applied using Adobe PDF Services.

Extracted tables are saved as CSV files.

Why Two Vectorstores?
Conflicts exist between text and table versions in some documents. Having separate stores ensures accurate, source-specific retrieval.

🛠️ Tools Used
Task	Tool / Library
Text Extraction	PyMuPDF
OCR (Image Tables)	Adobe PDF Services
Vector Store	FAISS
LLM for Answer Generation	chatbedrock – Claude 3.5 Sonnet
LLM for CSV Interpretation	chatbedrock – Mistral 7B Instruct
Embedding Model	amazon.titan-embed-text-v2:0
Storage	SQLite3

🚀 Potential Improvements
Use smarter OCR tools like LlamaParse, PDF.co, or Tesseract.

Add multi-agent orchestration to:

Grade retrieved chunks

Validate final responses

Implement metadata filtering for more relevant chunk retrieval.

Use fine-tuned models to:

Summarize long text documents (reduce token load)

Better interpret complex CSV tables

