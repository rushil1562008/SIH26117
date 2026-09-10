from pathlib import Path
from typing import Dict, Any, List, Optional
from tools.pdf_tool import pdf_tool
from tools.ocr_tool import ocr_tool
from tools.excel_tool import excel_tool
from tools.image_tool import image_tool

class MultimodalPipeline:
    """Fuses multi-source evidence (PDF, OCR, Excel, Images) into a coherent industrial context."""

    def process_inputs(
        self,
        pdf_path: Optional[Path] = None,
        image_path: Optional[Path] = None,
        excel_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        
        evidence_summary = []
        pdf_data = {}
        ocr_data = {}
        excel_data = {}
        image_data = {}

        if pdf_path and Path(pdf_path).exists():
            pdf_data = pdf_tool.extract(Path(pdf_path))
            evidence_summary.append(f"=== PDF INSPECTION REPORT ({pdf_data['filename']}) ===\n{pdf_data['full_text']}")

        if image_path and Path(image_path).exists():
            image_data = image_tool.analyze(Path(image_path))
            ocr_data = ocr_tool.extract_text(Path(image_path))
            evidence_summary.append(f"=== EQUIPMENT PHOTOGRAPH & VISUAL TELEMETRY ({image_data['filename']}) ===\n{image_data['visual_findings']}\n\nOCR Readings:\n{ocr_data['extracted_text']}")

        if excel_path and Path(excel_path).exists():
            excel_data = excel_tool.analyze(Path(excel_path))
            evidence_summary.append(f"=== MAINTENANCE HISTORY SPREADSHEET ({excel_data['filename']}) ===\n{excel_data['summary_text']}")

        fused_text = "\n\n".join(evidence_summary) if evidence_summary else "No multimodal files provided."

        return {
            "pdf": pdf_data,
            "ocr": ocr_data,
            "excel": excel_data,
            "image": image_data,
            "fused_evidence_text": fused_text,
        }

multimodal_pipeline = MultimodalPipeline()
