from pathlib import Path
from typing import Dict, Any, Optional
from app.config import config

def get_equipment_meta(state: Dict[str, Any]) -> Dict[str, str]:
    """Extracts standardized equipment metadata from state inputs and evidence."""
    paths_str = " ".join([
        str(state.get("pdf_path", "")),
        str(state.get("image_path", "")),
        str(state.get("excel_path", ""))
    ]).lower()
    
    task_str = str(state.get("task_description", "")).lower()

    # Priority 1: Exact file index patterns in input paths
    if "_02." in paths_str or "-02." in paths_str or "comp-201" in paths_str:
        return {
            "tag": "MRPL-COMP-201-A",
            "desc": "VDU Wet Gas Centrifugal Compressor",
            "unit": "VDU-2 (Vacuum Distillation Unit)",
            "short": "Compressor"
        }
    elif "_03." in paths_str or "-03." in paths_str or "hex-105" in paths_str:
        return {
            "tag": "MRPL-HEX-105-AB",
            "desc": "Crude vs Residue Shell & Tube Heat Exchanger",
            "unit": "CDU-1 Pre-Heat Train",
            "short": "Heat_Exchanger"
        }
    elif "_04." in paths_str or "-04." in paths_str or "col-301" in paths_str:
        return {
            "tag": "MRPL-COL-301",
            "desc": "Main Atmospheric Crude Distillation Column",
            "unit": "CDU-1 Atmospheric Fractionation",
            "short": "Distillation_Column"
        }
    elif "_05." in paths_str or "-05." in paths_str or "valve-402" in paths_str:
        return {
            "tag": "MRPL-VALVE-402-MOV",
            "desc": "Vacuum Residue Emergency Isolation Valve",
            "unit": "VDU Vacuum Residue Transfer",
            "short": "Control_Valve"
        }
    elif "_06." in paths_str or "-06." in paths_str or "boil-501" in paths_str:
        return {
            "tag": "MRPL-BOIL-501-HP",
            "desc": "Atmospheric Fired Heater & Radiant Steam Coil",
            "unit": "CDU-1 Furnace Section",
            "short": "Fired_Heater"
        }

    # Priority 2: Keywords in task description
    if "compressor" in task_str or "comp-201" in task_str:
        return {
            "tag": "MRPL-COMP-201-A",
            "desc": "VDU Wet Gas Centrifugal Compressor",
            "unit": "VDU-2 (Vacuum Distillation Unit)",
            "short": "Compressor"
        }
    elif "exchanger" in task_str or "hex-105" in task_str or "pre-heat" in task_str:
        return {
            "tag": "MRPL-HEX-105-AB",
            "desc": "Crude vs Residue Shell & Tube Heat Exchanger",
            "unit": "CDU-1 Pre-Heat Train",
            "short": "Heat_Exchanger"
        }
    elif "column" in task_str or "col-301" in task_str or "distillation" in task_str:
        return {
            "tag": "MRPL-COL-301",
            "desc": "Main Atmospheric Crude Distillation Column",
            "unit": "CDU-1 Atmospheric Fractionation",
            "short": "Distillation_Column"
        }
    elif "valve" in task_str or "valve-402" in task_str or "mov" in task_str:
        return {
            "tag": "MRPL-VALVE-402-MOV",
            "desc": "Vacuum Residue Emergency Isolation Valve",
            "unit": "VDU Vacuum Residue Transfer",
            "short": "Control_Valve"
        }
    elif "heater" in task_str or "boil-501" in task_str or "furnace" in task_str or "superheater" in task_str:
        return {
            "tag": "MRPL-BOIL-501-HP",
            "desc": "Atmospheric Fired Heater & Radiant Steam Coil",
            "unit": "CDU-1 Furnace Section",
            "short": "Fired_Heater"
        }

    return {
        "tag": "MRPL-PUMP-101-B",
        "desc": "Crude Feed Centrifugal Pump",
        "unit": "CDU-1 Atmospheric Distillation",
        "short": "Pump"
    }

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
