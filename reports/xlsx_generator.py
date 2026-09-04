import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from app.config import config

class XLSXReportGenerator:
    """Generates Excel structured maintenance summary deliverables."""

    def generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        output_filename = f"MRPL_Pump_Maintenance_Summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        out_path = config.output_dir / output_filename

        data = [
            {"Parameter": "Equipment Tag", "Value": "MRPL-PUMP-101-B"},
            {"Parameter": "Risk Level", "Value": state.get("risk_level", "HIGH")},
            {"Parameter": "Confidence Score", "Value": f"{state.get('confidence_score', 0.94)*100:.1f}%"},
            {"Parameter": "Approval Status", "Value": state.get("human_approval_status", "APPROVED")},
            {"Parameter": "Recommendation", "Value": state.get("recommendation", "")},
        ]
        df = pd.DataFrame(data)
        df.to_excel(out_path, index=False)

        return {"success": True, "filename": output_filename, "report_path": str(out_path)}

xlsx_generator = XLSXReportGenerator()
