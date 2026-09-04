import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent

class AppConfig(BaseModel):
    # Air-gap sovereignty flags
    air_gapped_mode: bool = Field(default=True)
    external_api_allowed: bool = Field(default=False)
    ollama_base_url: str = Field(default="http://127.0.0.1:11434")

    # Directories
    base_dir: Path = Field(default=BASE_DIR)
    data_dir: Path = Field(default=BASE_DIR / "data")
    knowledge_base_dir: Path = Field(default=BASE_DIR / "data" / "knowledge_base")
    documents_dir: Path = Field(default=BASE_DIR / "data" / "documents")
    images_dir: Path = Field(default=BASE_DIR / "data" / "images")
    tables_dir: Path = Field(default=BASE_DIR / "data" / "tables")
    output_dir: Path = Field(default=BASE_DIR / "outputs")
    log_dir: Path = Field(default=BASE_DIR / "logs")
    config_dir: Path = Field(default=BASE_DIR / "config")

    def ensure_directories(self):
        """Create necessary directories if they do not exist."""
        for d in [
            self.data_dir,
            self.knowledge_base_dir,
            self.documents_dir,
            self.images_dir,
            self.tables_dir,
            self.output_dir,
            self.log_dir,
            self.config_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

config = AppConfig()
config.ensure_directories()
