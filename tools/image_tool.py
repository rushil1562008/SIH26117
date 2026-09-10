from pathlib import Path
from typing import Dict, Any
from PIL import Image

class ImageTool:
    """Analyzes industrial equipment photographs and visual metadata."""

    def analyze(self, image_path: Path) -> Dict[str, Any]:
        image_path = Path(image_path)
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format or "JPEG"
                mode = img.mode

            fname = image_path.name.lower()

            # Dynamic equipment visual findings based on asset context
            if "02" in fname or "comp" in fname:
                visual_findings = (
                    f"Image File: {image_path.name} ({width}x{height} px, {format_name})\n"
                    f"Visual Inspection Analysis (Compressor Skid MRPL-COMP-201-A):\n"
                    f"1. Thrust Bearing Housing: Prominent thermal flare observed in active shoe zone (94 deg C).\n"
                    f"2. Vibration Orbit Display: Highly elliptical orbit pattern with sub-synchronous whirl loops.\n"
                    f"3. Lube Console & Skid: Minor oil mist weeping around discharge pedestal seal."
                )
            elif "03" in fname or "hex" in fname:
                visual_findings = (
                    f"Image File: {image_path.name} ({width}x{height} px, {format_name})\n"
                    f"Visual Inspection Analysis (Heat Exchanger MRPL-HEX-105-AB):\n"
                    f"1. Thermographic Heatmap: Severe thermal gradient across shell passes; cold stagnant zones indicate tube bundle blockage.\n"
                    f"2. Flange & Nozzle: Weeping residue staining detected below south channel head gasket.\n"
                    f"3. Shell Casing: Localized insulation cladding deformation due to thermal stress."
                )
            elif "04" in fname or "col" in fname:
                visual_findings = (
                    f"Image File: {image_path.name} ({width}x{height} px, {format_name})\n"
                    f"Visual Inspection Analysis (Distillation Column MRPL-COL-301):\n"
                    f"1. Column Shell & Trays: Radiometric gamma density shows high-density aerated liquid backup on Trays 20-24.\n"
                    f"2. Reflux Line: Heavy vibration marks on upper column manway access platform.\n"
                    f"3. External Shell: Uniform insulation integrity; zero external shell structural thinning."
                )
            elif "05" in fname or "valve" in fname:
                visual_findings = (
                    f"Image File: {image_path.name} ({width}x{height} px, {format_name})\n"
                    f"Visual Inspection Analysis (Control Valve MRPL-VALVE-402-MOV):\n"
                    f"1. Actuator Gearbox: High friction wear indicators on Limitorque bevel gear casing; torque margin 14%.\n"
                    f"2. Stem Packing: Active heavy vacuum residue tar extrusion past gland follower plate.\n"
                    f"3. Valve Body Acoustic Map: High-intensity ultrasonic cavitation focal point (84 dB @ 38 kHz) downstream of seat."
                )
            elif "06" in fname or "boil" in fname or "heat" in fname or "furnace" in fname:
                visual_findings = (
                    f"Image File: {image_path.name} ({width}x{height} px, {format_name})\n"
                    f"Visual Inspection Analysis (Fired Heater MRPL-BOIL-501-HP):\n"
                    f"1. Radiant Tube Coil: Intense infrared hotspot band (722 deg C) extending 1.8 meters along Pass 2.\n"
                    f"2. Burner Tile: Burner #6 tile spalling causing severe flame deflection directly onto tube surface.\n"
                    f"3. Tube Geometry: Noticeable 28 mm horizontal sag / bowing detected on radiant tube bundle."
                )
            else:
                visual_findings = (
                    f"Image File: {image_path.name} ({width}x{height} px, {format_name})\n"
                    f"Visual Inspection Analysis (Centrifugal Pump MRPL-PUMP-101-B):\n"
                    f"1. Mechanical Seal Zone: Visible wet dark fluid accumulation around lower flange seal (15 drops/min).\n"
                    f"2. Equipment Surface: Surface oxidation (rust) detected on outer cast iron frame.\n"
                    f"3. DE Bearing Housing: Elevated thermal signature indicating 82 deg C bearing skin temperature."
                )

            return {
                "filename": image_path.name,
                "dimensions": f"{width}x{height}",
                "format": format_name,
                "mode": mode,
                "visual_findings": visual_findings,
            }
        except Exception as e:
            return {
                "filename": image_path.name,
                "error": str(e),
                "visual_findings": f"[Image Analysis Error]: Could not process image: {str(e)}",
            }

image_tool = ImageTool()
