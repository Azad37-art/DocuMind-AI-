import os
import tempfile
from typing import List
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document

from project.config import CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_FILE_TYPES


def get_loader(file_path: str, file_extension: str):
    """Return the appropriate document loader based on file extension."""
    loaders = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".docx": Docx2txtLoader,
        ".csv": CSVLoader,
        ".md": UnstructuredMarkdownLoader,
    }
    loader_class = loaders.get(file_extension.lower())
    if loader_class is None:
        raise ValueError(f"Unsupported file type: {file_extension}")
    if file_extension.lower() == ".txt":
        return loader_class(file_path, encoding="utf-8", autodetect_encoding=True)
    return loader_class(file_path)


def load_document(uploaded_file) -> List[Document]:
    """Load and parse an uploaded Streamlit file object into LangChain Documents."""
    file_extension = Path(uploaded_file.name).suffix.lower()

    if file_extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            f"File type '{file_extension}' is not supported. "
            f"Supported types: {', '.join(SUPPORTED_FILE_TYPES)}"
        )

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=file_extension
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        loader = get_loader(tmp_path, file_extension)
        documents = loader.load()
    finally:
        os.unlink(tmp_path)

    for doc in documents:
        doc.metadata["source_filename"] = uploaded_file.name

    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into smaller chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    return chunks


def process_uploaded_file(uploaded_file) -> List[Document]:
    """Full pipeline: load file -> split into chunks."""
    documents = load_document(uploaded_file)
    chunks = split_documents(documents)
    return chunks