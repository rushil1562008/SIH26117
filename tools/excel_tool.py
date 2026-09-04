from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

class ExcelTool:
    """Reads Excel/CSV maintenance history spreadsheets and extracts key tabular evidence."""

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        file_path = Path(file_path)
        try:
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)

            columns = list(df.columns)
            row_count = len(df)
            head_records = df.head(5).to_dict(orient="records")
            summary_stats = df.describe(include="all").to_dict()

            summary_text = (
                f"Spreadsheet: {file_path.name} | Total Records: {row_count} | Columns: {', '.join(columns)}\n"
                f"Recent Maintenance Records:\n"
            )
            for i, rec in enumerate(head_records):
                summary_text += f"  Row {i+1}: {rec}\n"

            return {
                "filename": file_path.name,
                "columns": columns,
                "row_count": row_count,
                "sample_records": head_records,
                "summary_text": summary_text.strip(),
            }
        except Exception as e:
            return {
                "filename": file_path.name,
                "error": str(e),
                "summary_text": f"[Excel Reading Error]: {str(e)}",
            }

excel_tool = ExcelTool()
