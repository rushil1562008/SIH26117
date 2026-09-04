from pathlib import Path
from typing import Dict, Any, Optional
from app.config import config

class LocalFileTools:
    """Safe local file operations within project directories."""

    def read_file(self, file_path: Path) -> Dict[str, Any]:
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "content": "", "error": "File not found."}
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {"success": True, "content": content, "error": None}
        except Exception as e:
            return {"success": False, "content": "", "error": str(e)}

    def write_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "file_path": str(file_path), "error": None}
        except Exception as e:
            return {"success": False, "file_path": str(file_path), "error": str(e)}

file_tools = LocalFileTools()
