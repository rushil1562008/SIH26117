from pathlib import Path
from typing import Dict, Any, List

class PDFTool:
    """Local PDF extraction tool."""

    def extract(self, file_path: Path) -> Dict[str, Any]:
        file_path = Path(file_path)
        pages_content = []
        full_text = ""

        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_content.append({"page": i + 1, "text": text.strip()})
                full_text += f"\n--- Page {i+1} ---\n" + text.strip()
        except Exception as e:
            # Fallback to plain text reading if not a standard PDF
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    pages_content.append({"page": 1, "text": text.strip()})
                    full_text = text.strip()
            except Exception as ex:
                full_text = f"[PDF Parsing Error]: {str(ex)}"

        return {
            "filename": file_path.name,
            "page_count": len(pages_content),
            "pages": pages_content,
            "full_text": full_text.strip(),
        }

pdf_tool = PDFTool()
