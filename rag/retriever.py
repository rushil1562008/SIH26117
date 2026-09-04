from pathlib import Path
from typing import List, Dict, Any
from app.config import config
from rag.ingest import ingestor, DocumentIngestor
from rag.vector_store import vector_store, LocalVectorStore

class LocalRAGRetriever:
    """Manages document ingestion into knowledge base and semantic evidence retrieval with citations."""

    def __init__(self, doc_ingestor: DocumentIngestor = ingestor, store: LocalVectorStore = vector_store):
        self.ingestor = doc_ingestor
        self.store = store
        self.auto_index_knowledge_base()

    def auto_index_knowledge_base(self):
        """Indexes all files currently present in data/knowledge_base/."""
        kb_path = config.knowledge_base_dir
        if not kb_path.exists():
            return

        for file_path in kb_path.glob("*.*"):
            if file_path.suffix.lower() in [".pdf", ".txt", ".md", ".docx"]:
                self.index_file(file_path)

    def index_file(self, file_path: Path):
        """Chunks and indexes a specific file into the local vector store."""
        chunks = self.ingestor.chunk_document(file_path)
        self.store.add_chunks(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves semantic search results with citation metadata."""
        raw_results = self.store.search(query, top_k=top_k)
        formatted_evidence = []
        for doc, score in raw_results:
            formatted_evidence.append({
                "source_citation": f"{doc['filename']} — Page {doc['page']}",
                "filename": doc["filename"],
                "page": doc["page"],
                "chunk_id": doc["chunk_id"],
                "score": round(score, 4),
                "text": doc["text"],
            })
        return formatted_evidence

retriever = LocalRAGRetriever()
