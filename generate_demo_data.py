import os
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from app.config import config

def create_synthetic_demo_files():
    """Generates synthetic non-confidential industrial demo files for MRPL Golden Demo."""
    config.ensure_directories()
    
    docs_dir = config.documents_dir
    img_dir = config.images_dir
    tb_dir = config.tables_dir
    kb_dir = config.knowledge_base_dir

    print("Generating synthetic demo files...")

    # 1. Inspection Report PDF / TXT
    pdf_path = docs_dir / "sample_pump_inspection.pdf"
    pdf_text_content = (
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)\n"
        "EQUIPMENT INSPECTION REPORT — CDU UNIT 1\n"
        "Equipment ID: MRPL-PUMP-101-B\n"
        "Equipment Description: Crude Feed Centrifugal Pump\n"
        "Inspection Date: 2026-09-02\n\n"
        "OBSERVATIONS:\n"
        "- Drive-End Bearing Housing Temperature: 82°C (Warning threshold: 75°C).\n"
        "- Mechanical Seal Zone: Active seal flush oil leakage observed at 15 drops/min.\n"
        "- Overall Vibration Level: 4.8 mm/s RMS (SOP limit: 4.5 mm/s).\n"
        "- Acoustic Inspection: Audible high-frequency bearing clicking noise.\n\n"
        "INSPECTOR RECOMMENDATION:\n"
        "Urgent maintenance inspection required to prevent bearing seizure and unplanned shutdown."
    )
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        y = 750
        for line in pdf_text_content.split("\n"):
            c.drawString(72, y, line)
            y -= 15
        c.save()
        print(f"Created: {pdf_path}")
    except Exception:
        # Fallback to text file if reportlab unavailable
        pdf_path = docs_dir / "sample_pump_inspection.txt"
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(pdf_text_content)
        print(f"Created: {pdf_path}")

    # 2. Maintenance SOP PDF in Knowledge Base
    sop_path = kb_dir / "sample_maintenance_sop.pdf"
    sop_content = (
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)\n"
        "STANDARD OPERATING PROCEDURE: CENTRIFUGAL PUMP OVERHAUL (SOP-MRPL-MECH-402)\n"
        "Document Version: 3.1 | Classification: Internal SOP\n\n"
        "SECTION 4.2: BEARING & MECHANICAL SEAL OPERATIONAL THRESHOLDS\n"
        "Page 12\n"
        "1. Temperature Limits: Maximum allowable drive-end bearing operating temperature is 75°C. "
        "Temperatures exceeding 80°C require immediate plant notification and scheduled shutdown within 48 hours.\n"
        "2. Vibration Thresholds: Vibration levels exceeding 4.5 mm/s RMS indicate severe mechanical unbalance or bearing fatigue.\n"
        "3. Mechanical Seal Leakage: Any mechanical seal leakage exceeding 5 drops/min requires seal cartridge replacement and oil flush.\n"
        "4. Maintenance Frequency: Main drive bearings must undergo full overhaul every 12 months under continuous crude service."
    )

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(sop_path), pagesize=letter)
        y = 750
        for line in sop_content.split("\n"):
            c.drawString(72, y, line)
            y -= 15
        c.save()
        print(f"Created: {sop_path}")
    except Exception:
        sop_path = kb_dir / "sample_maintenance_sop.txt"
        with open(sop_path, "w", encoding="utf-8") as f:
            f.write(sop_content)
        print(f"Created: {sop_path}")

    # 3. Maintenance History Excel
    excel_path = tb_dir / "sample_maintenance_history.xlsx"
    maint_data = [
        {"Record ID": "REC-8841", "Date": "2025-07-10", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Bearing Replacement & Seal Flush", "Technician": "K. Sharma", "Status": "Completed"},
        {"Record ID": "REC-8920", "Date": "2025-11-15", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Routine Lubrication & Vibration Check", "Technician": "R. Patil", "Status": "Completed"},
        {"Record ID": "REC-9102", "Date": "2026-03-04", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Coupling Alignment", "Technician": "A. Verma", "Status": "Completed"},
        {"Record ID": "REC-9350", "Date": "2026-07-20", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Oil Top-up & Gasket Inspection", "Technician": "M. Kumar", "Status": "Completed"},
    ]
    df = pd.DataFrame(maint_data)
    df.to_excel(excel_path, index=False)
    print(f"Created: {excel_path}")

    # 4. Pump Photo Image JPG
    img_path = img_dir / "sample_pump_image.jpg"
    img = Image.new("RGB", (600, 400), color=(40, 50, 70))
    draw = ImageDraw.Draw(img)
    
    # Draw equipment outline and visual markers
    draw.rectangle([50, 50, 550, 350], outline=(200, 200, 200), width=4)
    draw.rectangle([100, 100, 300, 300], fill=(70, 80, 100), outline=(255, 100, 100), width=3)
    draw.ellipse([350, 120, 500, 270], fill=(90, 60, 60), outline=(255, 50, 50), width=4)
    
    # Text annotation overlays
    draw.text((60, 60), "EQUIPMENT TAG: MRPL-PUMP-101-B", fill=(255, 255, 255))
    draw.text((110, 110), "MECHANICAL SEAL ZONE\n(OIL LEAK DETECTED)", fill=(255, 150, 150))
    draw.text((360, 130), "BEARING HOUSING\n(82°C HIGH TEMP)", fill=(255, 200, 100))

    img.save(img_path)
    print(f"Created: {img_path}")

    print("All synthetic demo data generated successfully!")

if __name__ == "__main__":
    create_synthetic_demo_files()
