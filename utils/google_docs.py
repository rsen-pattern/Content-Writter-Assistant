"""Google Docs export – creates a formatted document from markdown content."""

from __future__ import annotations
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def create_google_doc(
    title: str,
    markdown_content: str,
    credentials: Credentials,
    share_email: str = "",
) -> str:
    """Create a Google Doc from markdown content.

    Returns the document URL.
    """
    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    # Create blank document
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Convert markdown to Google Docs requests
    requests = _markdown_to_docs_requests(markdown_content)

    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    # Share if email provided
    if share_email:
        drive_service.permissions().create(
            fileId=doc_id,
            body={
                "type": "user",
                "role": "writer",
                "emailAddress": share_email,
            },
            sendNotificationEmail=True,
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def _markdown_to_docs_requests(markdown: str) -> list[dict]:
    """Convert markdown text to Google Docs API batchUpdate requests."""
    requests = []
    index = 1  # Google Docs index starts at 1

    lines = markdown.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Heading detection
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2) + "\n"

            requests.append({
                "insertText": {"location": {"index": index}, "text": text}
            })

            heading_style = {
                1: "HEADING_1",
                2: "HEADING_2",
                3: "HEADING_3",
                4: "HEADING_4",
                5: "HEADING_5",
                6: "HEADING_6",
            }.get(level, "HEADING_6")

            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + len(text)},
                    "paragraphStyle": {"namedStyleType": heading_style},
                    "fields": "namedStyleType",
                }
            })
            index += len(text)
            i += 1
            continue

        # Regular paragraph
        text = line + "\n"
        requests.append({
            "insertText": {"location": {"index": index}, "text": text}
        })

        # Handle bold/italic within the text
        bold_ranges = _find_markdown_ranges(line, r"\*\*(.+?)\*\*", index)
        italic_ranges = _find_markdown_ranges(line, r"\*(.+?)\*", index)

        for start, end in bold_ranges:
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {"bold": True},
                    "fields": "bold",
                }
            })

        for start, end in italic_ranges:
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end},
                    "textStyle": {"italic": True},
                    "fields": "italic",
                }
            })

        index += len(text)
        i += 1

    return requests


def _find_markdown_ranges(
    line: str, pattern: str, base_index: int
) -> list[tuple[int, int]]:
    """Find text ranges for markdown formatting patterns."""
    ranges = []
    for match in re.finditer(pattern, line):
        start = base_index + match.start()
        end = base_index + match.end()
        ranges.append((start, end))
    return ranges


def export_markdown_fallback(
    sections: dict[str, str],
) -> str:
    """Combine all sections into a single markdown document for download."""
    parts = []
    for title, content in sections.items():
        if content:
            parts.append(f"# {title}\n\n{content}")
    return "\n\n---\n\n".join(parts)
