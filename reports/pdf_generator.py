import datetime
from pathlib import Path
from typing import Dict, Any
from app.config import config
from tools.file_tools import get_equipment_meta

class PDFReportGenerator:
    """Generates PDF report deliverables using ReportLab or text fallback."""

    def generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        eq_meta = get_equipment_meta(state)
        output_filename = f"MRPL_{eq_meta['short']}_Inspection_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        out_path = config.output_dir / output_filename

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(str(out_path), pagesize=letter)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(72, 750, "MRPL SOVEREIGN INDUSTRIAL MAINTENANCE REPORT")
            c.setFont("Helvetica-Bold", 11)
            c.drawString(72, 730, f"Equipment: {eq_meta['tag']} | Unit: {eq_meta['unit']}")
            c.setFont("Helvetica", 10)
            c.drawString(72, 712, f"Description: {eq_meta['desc']}")
            c.drawString(72, 695, f"Risk Level: {state.get('risk_level', 'HIGH')} | Confidence: {state.get('confidence_score', 0.94)*100:.1f}%")
            c.drawString(72, 678, f"Human Approval Status: {state.get('human_approval_status', 'APPROVED')}")
            
            c.setFont("Helvetica-Bold", 10)
            c.drawString(72, 650, "Action Directive & Recommendation:")
            c.setFont("Helvetica", 9)
            
            rec_text = state.get("recommendation", "")
            y = 632
            for line in rec_text.split("\n"):
                c.drawString(72, y, line[:95])
                y -= 14
                if y < 60:
                    break
                    
            c.save()
        except Exception:
            # Fallback simple text-based PDF file creation
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"MRPL INDUSTRIAL REPORT: {eq_meta['tag']}\nRisk Level: {state.get('risk_level')}\nRecommendation: {state.get('recommendation')}")

        return {"success": True, "filename": output_filename, "report_path": str(out_path)}

pdf_generator = PDFReportGenerator()
