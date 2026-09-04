import datetime
from pathlib import Path
from typing import Dict, Any
from app.config import config

class PDFReportGenerator:
    """Generates PDF report deliverables using ReportLab or text fallback."""

    def generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        output_filename = f"MRPL_Pump_Inspection_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        out_path = config.output_dir / output_filename

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(str(out_path), pagesize=letter)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, 750, "MRPL SOVEREIGN INDUSTRIAL REPORT (PDF)")
            c.setFont("Helvetica", 10)
            c.drawString(100, 730, f"Equipment: MRPL-PUMP-101-B | Risk: {state.get('risk_level', 'HIGH')}")
            c.drawString(100, 710, f"Approval Status: {state.get('human_approval_status', 'APPROVED')}")
            c.drawString(100, 680, "Recommendation Summary:")
            c.drawString(100, 660, state.get("recommendation", "")[:90])
            c.save()
        except Exception:
            # Fallback simple text-based PDF file creation
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"MRPL INDUSTRIAL REPORT (PDF Fallback)\nRisk Level: {state.get('risk_level')}\nRecommendation: {state.get('recommendation')}")

        return {"success": True, "filename": output_filename, "report_path": str(out_path)}

pdf_generator = PDFReportGenerator()
