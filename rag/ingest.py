import os
from pathlib import Path
from typing import List, Dict, Any
from app.config import config

class DocumentIngestor:
    """Ingests PDFs, text files, SOPs, and manuals into structured chunks with rich metadata."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def read_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Reads a PDF file page by page using pypdf or PyPDF2 if available."""
        pages = []
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({"page_num": i + 1, "text": text.strip()})
        except Exception:
            # Fallback text reading if PDF parser fails or file is plain text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                pages.append({"page_num": 1, "text": content.strip()})

        return pages

    def chunk_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Splits document into chunks with file metadata."""
        file_path = Path(file_path)
        filename = file_path.name
        chunks = []

        if file_path.suffix.lower() == ".pdf":
            pages = self.read_pdf(file_path)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                pages = [{"page_num": 1, "text": f.read()}]

        chunk_counter = 1
        for page_info in pages:
            text = page_info["text"]
            page_num = page_info["page_num"]
            
            if not text:
                continue

            # Simple sliding window chunker
            words = text.split()
            start = 0
            while start < len(words):
                end = start + self.chunk_size
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)

                chunks.append({
                    "chunk_id": f"{filename}_p{page_num}_c{chunk_counter}",
                    "filename": filename,
                    "page": page_num,
                    "text": chunk_text,
                    "source_location": f"{filename} - Page {page_num}",
                    "file_path": str(file_path),
                })
                chunk_counter += 1
                start += (self.chunk_size - self.chunk_overlap)

        return chunks

ingestor = DocumentIngestor()
