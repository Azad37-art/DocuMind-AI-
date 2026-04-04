import os
from typing import List, Optional
from typing import List, Dict

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from project.config import EMBEDDING_MODEL, FAISS_INDEX_PATH, MAX_RETRIEVAL_DOCS


def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialize and return the HuggingFace embedding model."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return embeddings


def create_vector_store(chunks: List[Document]) -> FAISS:
    """Create a FAISS vector store from document chunks."""
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store


def save_vector_store(vector_store: FAISS, path: str = FAISS_INDEX_PATH) -> None:
    """Save the FAISS index to disk."""
    os.makedirs(path, exist_ok=True)
    vector_store.save_local(path)


def load_vector_store(path: str = FAISS_INDEX_PATH) -> Optional[FAISS]:
    """Load a FAISS index from disk. Returns None if not found."""
    if not os.path.exists(path):
        return None
    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        path, embeddings, allow_dangerous_deserialization=True
    )
    return vector_store




def get_retriever(vector_store: FAISS, k: int = MAX_RETRIEVAL_DOCS):
    """Get a retriever from the vector store."""
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def similarity_search(
    vector_store: FAISS, query: str, k: int = MAX_RETRIEVAL_DOCS
) -> List[Document]:
    """Perform similarity search and return relevant documents."""
    results = vector_store.similarity_search(query, k=k)
    return results



def get_timestamp() -> str:
    """Return current time formatted as HH:MM."""
    return datetime.now().strftime("%H:%M")


def truncate_text(text: str, max_length: int = 300) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def format_sources(sources: List[Dict]) -> str:
    """Format source documents into a readable string."""
    if not sources:
        return ""
    lines = []
    for i, source in enumerate(sources, 1):
        filename = source.get("filename", "Unknown")
        page = source.get("page")
        snippet = source.get("snippet", "")
        page_info = f" (Page {page + 1})" if page is not None else ""
        lines.append(f"**Source {i}:** {filename}{page_info}")
        if snippet:
            lines.append(f"> {truncate_text(snippet, 200)}")
        lines.append("")
    return "\n".join(lines)


def count_tokens_approx(text: str) -> int:
    """Approximate token count (1 token ≈ 4 characters)."""
    return len(text) // 4


def validate_api_key(api_key: str) -> bool:
    """Basic validation that an API key is not empty."""
    return bool(api_key and api_key.strip())
