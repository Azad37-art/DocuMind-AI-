import re
from typing import List, Dict
from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"


def sanitize_text(text: str) -> str:
    """Remove excessive whitespace and normalize text."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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