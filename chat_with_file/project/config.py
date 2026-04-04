import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

FAISS_INDEX_PATH = "faiss_index"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
MAX_RETRIEVAL_DOCS = 3

SUPPORTED_FILE_TYPES = [".pdf", ".txt", ".docx", ".csv", ".md"]
MAX_FILE_SIZE_MB = 50

TEMPERATURE = 0.3
MAX_OUTPUT_TOKENS = 8000