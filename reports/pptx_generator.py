import datetime
from pathlib import Path
from typing import Dict, Any
from pptx import Presentation
from pptx.util import Inches, Pt
from app.config import config

class PPTXReportGenerator:
    """Generates PowerPoint presentation summary deliverables."""

    def generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "MRPL Industrial Maintenance Report"
        subtitle.text = f"Equipment: MRPL-PUMP-101-B\nRisk: {state.get('risk_level', 'HIGH')} | Status: {state.get('human_approval_status', 'APPROVED')}"

        output_filename = f"MRPL_Pump_Inspection_Presentation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        out_path = config.output_dir / output_filename
        prs.save(out_path)

        return {"success": True, "filename": output_filename, "report_path": str(out_path)}

pptx_generator = PPTXReportGenerator()
