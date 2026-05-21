"""Parse uploaded brief files into markdown text.

Accepted formats: .md, .markdown, .txt, .docx. Falls back to UTF-8 decoding for
unknown text-like extensions.
"""

from __future__ import annotations
from typing import IO


def _docx_to_markdown(file_like: IO[bytes]) -> str:
    """Convert a .docx upload into lightweight markdown (headings + paragraphs + lists)."""
    from docx import Document

    doc = Document(file_like)
    lines: list[str] = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            lines.append("")
            continue

        style = (para.style.name or "").lower()
        if style.startswith("heading"):
            # "Heading 1" -> "# ", "Heading 2" -> "## ", etc.
            level = "".join(c for c in style if c.isdigit())
            try:
                depth = max(1, min(int(level), 6))
            except ValueError:
                depth = 2
            lines.append(f"{'#' * depth} {text}")
        elif style == "list bullet" or style.startswith("list bullet"):
            lines.append(f"- {text}")
        elif style == "list number" or style.startswith("list number"):
            lines.append(f"1. {text}")
        else:
            lines.append(text)

    # Append tables as pipe tables
    for table in doc.tables:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            rows.append("| " + " | ".join(cells) + " |")
        if rows:
            header = rows[0]
            separator = "| " + " | ".join("---" for _ in table.rows[0].cells) + " |"
            lines.extend(["", header, separator, *rows[1:]])

    return "\n".join(lines).strip()


def extract_brief_text(uploaded_file) -> str:
    """Return brief text as markdown from a Streamlit UploadedFile.

    Raises ValueError on unsupported file types or empty content.
    """
    if uploaded_file is None:
        raise ValueError("No file provided.")

    name = (uploaded_file.name or "").lower()
    if name.endswith(".docx"):
        text = _docx_to_markdown(uploaded_file)
    elif name.endswith((".md", ".markdown", ".txt")):
        raw = uploaded_file.read()
        text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
    else:
        # Last-resort: try to decode as text
        try:
            raw = uploaded_file.read()
            text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
        except Exception as e:
            raise ValueError(f"Unsupported file type: {uploaded_file.name}") from e

    text = text.strip()
    if not text:
        raise ValueError("Uploaded file is empty.")
    return text
