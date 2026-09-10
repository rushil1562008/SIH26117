import os
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.config import config

def draw_gauge(draw, center, radius, value, min_val, max_val, title, unit=""):
    """Helper to draw a circular industrial dial gauge on PIL image."""
    cx, cy = center
    # Outer circle
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(30, 35, 45), outline=(180, 190, 200), width=2)
    # Ticks / Arc
    angle_norm = (value - min_val) / max(1e-5, (max_val - min_val))
    angle_norm = max(0.0, min(1.0, angle_norm))
    # Map 0..1 to 135 deg .. 405 deg (or -135 .. +135)
    import math
    angle_rad = math.radians(135 + angle_norm * 270)
    pointer_len = radius * 0.75
    px = cx + pointer_len * math.cos(angle_rad)
    py = cy + pointer_len * math.sin(angle_rad)
    
    # Gauge pointer
    pointer_color = (255, 60, 60) if angle_norm > 0.75 else (80, 220, 100)
    draw.line([(cx, cy), (px, py)], fill=pointer_color, width=3)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    
    # Labels
    draw.text((cx - radius + 10, cy + radius - 22), f"{title}", fill=(200, 210, 220))
    draw.text((cx - radius + 10, cy + radius - 10), f"{value} {unit}", fill=pointer_color)

def create_synthetic_demo_files():
    """Generates synthetic industrial demo files for MRPL Golden Demo (23 total: 4 baseline + 19 new)."""
    config.ensure_directories()
    
    docs_dir = config.documents_dir
    img_dir = config.images_dir
    tb_dir = config.tables_dir
    kb_dir = config.knowledge_base_dir

    print("Generating comprehensive synthetic refinery demo files...")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        has_reportlab = True
    except Exception:
        has_reportlab = False

    def write_pdf(file_path: Path, content_lines: list):
        if has_reportlab:
            c = canvas.Canvas(str(file_path), pagesize=letter)
            y = 750
            for line in content_lines:
                if line.startswith("==="):
                    c.setFont("Helvetica-Bold", 11)
                    y -= 6
                elif line.startswith("MRPL") or "REPORT" in line or "PROCEDURE" in line or "MANUAL" in line or "FMEA" in line:
                    c.setFont("Helvetica-Bold", 10)
                elif ":" in line and len(line.split(":")[0]) < 25:
                    c.setFont("Helvetica-Bold", 9)
                else:
                    c.setFont("Helvetica", 9)
                
                # Check page overflow
                if y < 45:
                    c.showPage()
                    y = 750
                    c.setFont("Helvetica", 9)
                
                c.drawString(54, y, line[:100])
                y -= 13
            c.save()
            print(f"Created PDF: {file_path.name}")
        else:
            txt_path = file_path.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content_lines))
            print(f"Created Fallback TXT: {txt_path.name}")

    # =========================================================================
    # BASELINE FILES (Index 01 / sample_*)
    # =========================================================================
    
    # 1.1 documents/sample_pump_inspection.pdf
    write_pdf(docs_dir / "sample_pump_inspection.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "EQUIPMENT INSPECTION REPORT - CDU UNIT 1",
        "=======================================================================",
        "Equipment ID: MRPL-PUMP-101-B",
        "Equipment Description: Crude Feed Centrifugal Pump",
        "Operating Unit: CDU-1 (Atmospheric Distillation Unit)",
        "Inspection Date: 2026-09-02",
        "Lead Mechanical Inspector: S. Ramanathan (Emp #44102)",
        "",
        "CRITICAL OBSERVATIONS:",
        "- Drive-End (DE) Bearing Housing Temperature: 82 deg C (High Alarm limit: 75 deg C).",
        "- Non-Drive End (NDE) Bearing Temperature: 64 deg C (Normal).",
        "- Mechanical Seal Zone: Active seal flush oil leakage observed at 15 drops/min.",
        "- Overall Vibration Velocity: 4.8 mm/s RMS (ISO 10816 Class II Limit: 4.5 mm/s RMS).",
        "- Acoustic Inspection: Audible high-frequency bearing cage clicking noise.",
        "- Casing Integrity: Surface oxidation and oil staining on foundation skirt.",
        "",
        "OPERATIONAL IMPACT & RISK RATING: HIGH",
        "Risk of unexpected bearing seizure and crude feed loss causing CDU furnace trip.",
        "",
        "INSPECTOR RECOMMENDATION:",
        "1. Schedule urgent maintenance intervention within 48 hours.",
        "2. Replace Drive-End angular contact ball bearing assembly (SKF 7314 BECBM).",
        "3. Replace mechanical seal cartridge assembly (Plan 53A dual pressurized seal).",
        "4. Perform laser coupling alignment and lube oil flushing before restart."
    ])

    # 1.2 knowledge_base/sample_maintenance_sop.pdf
    write_pdf(kb_dir / "sample_maintenance_sop.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "STANDARD OPERATING PROCEDURE: CENTRIFUGAL PUMP OVERHAUL (SOP-MRPL-MECH-402)",
        "Document Version: 3.1 | Classification: Internal SOP | Custodian: Mechanical Reliability",
        "=======================================================================",
        "SECTION 4.0: OPERATING THRESHOLDS & SAFE OPERATING WINDOWS (SOW)",
        "4.1 Scope: Applicable to all API 610 single/multi-stage centrifugal pumps in CDU/VDU.",
        "4.2 Bearing Temperature Limits:",
        "    - Normal Continuous Range: 45 deg C to 70 deg C.",
        "    - Advisory Warning Threshold: 75 deg C.",
        "    - High Trip / Shutdown Mandate: Exceeding 80 deg C requires plant notification",
        "      and scheduled shutdown within 48 hours to avert catastrophic shaft seizure.",
        "",
        "4.3 Vibration Severity Criteria (ISO 10816-3 Group 1/2 Rigid Mount):",
        "    - Zone A (Good): 0.0 - 2.8 mm/s RMS.",
        "    - Zone B (Acceptable): 2.8 - 4.5 mm/s RMS.",
        "    - Zone C (Unrestricted Operation Not Permitted / Alarm): > 4.5 mm/s RMS.",
        "    - Zone D (Trip / Immediate Danger): > 7.1 mm/s RMS.",
        "",
        "4.4 Mechanical Seal Integrity (API 682 Standard):",
        "    - Normal barrier fluid leakage: < 2 drops/min.",
        "    - Leakage exceeding 5 drops/min indicates primary face degradation.",
        "    - Active leakage at 15 drops/min demands cartridge replacement and barrier flush.",
        "",
        "4.5 Overhaul Intervals: Full rotating assembly overhaul every 12 months in crude service."
    ])

    # 1.3 tables/sample_maintenance_history.xlsx
    df_sample_tb = pd.DataFrame([
        {"Record ID": "REC-8841", "Date": "2025-07-10", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Bearing Replacement & Seal Flush", "Technician": "K. Sharma", "Status": "Completed", "Cost_INR": 42000, "Downtime_Hrs": 14},
        {"Record ID": "REC-8920", "Date": "2025-11-15", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Routine Lubrication & Vibration Check", "Technician": "R. Patil", "Status": "Completed", "Cost_INR": 8500, "Downtime_Hrs": 2},
        {"Record ID": "REC-9102", "Date": "2026-03-04", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Coupling Alignment & Shimming", "Technician": "A. Verma", "Status": "Completed", "Cost_INR": 15000, "Downtime_Hrs": 4},
        {"Record ID": "REC-9350", "Date": "2026-07-20", "Equipment Tag": "MRPL-PUMP-101-B", "Action": "Oil Top-up & Gasket Inspection", "Technician": "M. Kumar", "Status": "Completed", "Cost_INR": 6200, "Downtime_Hrs": 1},
    ])
    df_sample_tb.to_excel(tb_dir / "sample_maintenance_history.xlsx", index=False)
    print("Created: sample_maintenance_history.xlsx")

    # 1.4 images/sample_pump_image.jpg
    img1 = Image.new("RGB", (650, 420), color=(25, 32, 45))
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([20, 20, 630, 400], outline=(100, 120, 150), width=2)
    d1.rectangle([70, 70, 580, 110], fill=(35, 45, 65))
    d1.text((80, 85), "MRPL REFINERY - CDU1 CRUDE FEED PUMP (MRPL-PUMP-101-B)", fill=(255, 255, 255))
    # Pump housing graphic
    d1.rectangle([100, 150, 320, 340], fill=(50, 65, 85), outline=(220, 80, 80), width=3)
    d1.ellipse([340, 170, 520, 320], fill=(70, 50, 50), outline=(255, 70, 70), width=3)
    d1.text((115, 170), "MECHANICAL SEAL ZONE\nActive Leak: 15 drops/min\nFLANGE LEAK DETECTED", fill=(255, 160, 160))
    d1.text((360, 190), "DE BEARING HOUSING\nMeasured Temp: 82 deg C\nALARM LIMIT: 75 deg C", fill=(255, 220, 100))
    draw_gauge(d1, (560, 240), 45, 82, 0, 120, "DE Temp", "C")
    img1.save(img_dir / "sample_pump_image.jpg", quality=92)
    print("Created: sample_pump_image.jpg")

    # =========================================================================
    # 19 NEW FILES: ASSETS 02 THROUGH 06
    # =========================================================================

    # -------------------------------------------------------------------------
    # ASSET 02: VDU WET GAS CENTRIFUGAL COMPRESSOR (MRPL-COMP-201-A)
    # -------------------------------------------------------------------------
    # Document: pump_inspection_02.pdf
    write_pdf(docs_dir / "pump_inspection_02.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "ROTATING MACHINERY INSPECTION REPORT - VDU UNIT 2",
        "=======================================================================",
        "Equipment ID: MRPL-COMP-201-A",
        "Equipment Description: VDU Wet Gas Multi-Stage Centrifugal Compressor",
        "Operating Unit: VDU-2 (Vacuum Distillation Overhead Section)",
        "Inspection Date: 2026-09-08",
        "Inspector: J. B. Hegde (Senior Reliability Specialist, API 617 Certified)",
        "",
        "OBSERVATIONS & VIBRATION SPECTRUM ANALYSIS:",
        "- Thrust Bearing Active Face Temperature: 94 deg C (Max Limit: 88 deg C).",
        "- Stage-1 Radial Shaft Vibration (Probe X): 6.8 mm/s RMS (Alarm Limit: 4.5 mm/s).",
        "- Stage-1 Radial Shaft Vibration (Probe Y): 6.4 mm/s RMS.",
        "- Sub-synchronous Vibration (0.43X Running Speed): Oil whirl / hydrodynamic instability detected.",
        "- Lube Oil Differential Pressure (Delta-P): Dropped to 0.72 bar (Normal range: 1.2 - 1.6 bar).",
        "- Dry Gas Seal Nitrogen Buffer Flow: Elevated at 18.5 Nm3/h (Normal baseline: < 10 Nm3/h).",
        "",
        "ROOT CAUSE HYPOTHESIS:",
        "Lube oil viscosity degradation combined with severe labyrinth seal contamination leading",
        "to hydrodynamic journal bearing destabilization and incipient axial thrust collar scrubbing.",
        "",
        "MAINTENANCE DIRECTIVE & SAFETY CLASS: CRITICAL (LEVEL 1)",
        "1. Immediate load reduction on VDU-2 by 25% to throttle suction volumetric flow.",
        "2. Emergency shutdown within 24 hours to prevent catastropic rotor-stator contact.",
        "3. Replace tilting-pad thrust bearing shoes and perform high-pressure lube filter swap.",
        "4. Overhaul Dry Gas Seal (DGS) cartridge #1 and restore N2 buffer differential."
    ])

    # Knowledge Base: maintenance_sop_02.pdf
    write_pdf(kb_dir / "maintenance_sop_02.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "TECHNICAL MANUAL & SOP: CENTRIFUGAL COMPRESSOR RELIABILITY (SOP-MRPL-COMP-501)",
        "Document Version: 4.0 | Standard: API 617 8th Edition | Classification: Controlled",
        "=======================================================================",
        "SECTION 1: VIBRATION TRIPPING CRITERIA & RUNNING CLEARANCES",
        "1.1 Radial Shaft Vibration Thresholds (Proximity Probes):",
        "    - Alert Alarm: 4.5 mm/s RMS (or 45 micrometers peak-to-peak).",
        "    - Emergency Automatic Trip: 7.1 mm/s RMS (or 65 micrometers peak-to-peak).",
        "    - Spectral Analysis Protocol: Any presence of sub-synchronous peaks between",
        "      0.40X and 0.48X running speed indicates oil whirl; immediately verify lube temp.",
        "",
        "SECTION 2: LUBRICATING OIL & BEARING TEMPERATURE SPECIFICATIONS",
        "2.1 Lubricant Spec: ISO VG 46 Turbine Oil with rust/oxidation inhibitors (ASTM D4304).",
        "2.2 Lube Oil Header Pressure: 1.8 to 2.4 bar gauge. Filter Delta-P limit: 1.0 bar max.",
        "2.3 Bearing Temperature Limits:",
        "    - Journal Bearings: Max allowable 90 deg C. Trip at 100 deg C.",
        "    - Active Thrust Bearing Face: Max continuous 88 deg C. Trip at 98 deg C.",
        "",
        "SECTION 3: DRY GAS SEALS (DGS) & BARRIER SYSTEM",
        "3.1 Buffer Gas (N2) Supply Pressure: Must be minimum 3.0 bar above internal seal cavity.",
        "3.2 Primary vent leakage exceeding 12 Nm3/h indicates primary seal face micro-scoring.",
        "",
        "SECTION 4: TROUBLESHOOTING GUIDE (FMEA CROSS-REFERENCE)",
        "Failure Mode: High Radial Vibration + Oil Whirl.",
        "Corrective Actions: (a) Increase lube oil supply temp to 45C to reduce viscosity,",
        "(b) Verify tilting pad pivot clearances, (c) Check shaft balance & alignment."
    ])

    # Table: maintenance_history_02.xlsx
    maint_rows_02 = [
        {"Log_ID": "LOG-COMP-101", "Date": "2025-06-12", "Asset_Tag": "MRPL-COMP-201-A", "Component": "Dry Gas Seal Cartridge", "Intervention": "Replaced Primary Seal Ring", "Technician": "V. Kulkarni", "Vibration_RMS_Post": 2.1, "Lube_Temp_C": 58, "Status": "Closed"},
        {"Log_ID": "LOG-COMP-142", "Date": "2025-10-04", "Asset_Tag": "MRPL-COMP-201-A", "Component": "Lube Oil Console", "Intervention": "Duplex Filter Cartridge Swap", "Technician": "T. Nair", "Vibration_RMS_Post": 2.4, "Lube_Temp_C": 61, "Status": "Closed"},
        {"Log_ID": "LOG-COMP-219", "Date": "2026-02-18", "Asset_Tag": "MRPL-COMP-201-A", "Component": "Tilting Pad Journal", "Intervention": "Clearance Inspection & Shimming", "Technician": "S. Desai", "Vibration_RMS_Post": 3.2, "Lube_Temp_C": 68, "Status": "Closed"},
        {"Log_ID": "LOG-COMP-308", "Date": "2026-06-25", "Asset_Tag": "MRPL-COMP-201-A", "Component": "Coupling Diaphragm", "Intervention": "Laser Alignment & Bolt Torquing", "Technician": "V. Kulkarni", "Vibration_RMS_Post": 3.6, "Lube_Temp_C": 72, "Status": "Closed"},
        {"Log_ID": "LOG-COMP-390", "Date": "2026-09-08", "Asset_Tag": "MRPL-COMP-201-A", "Component": "Thrust Bearing", "Intervention": "Emergency Inspection - High Temp/Vib", "Technician": "J. B. Hegde", "Vibration_RMS_Post": 6.8, "Lube_Temp_C": 94, "Status": "Active Alert"},
    ]
    # Hourly telemetry sensor data sheet
    telemetry_rows_02 = []
    base_time = pd.Timestamp("2026-09-08 00:00:00")
    for hour in range(24):
        vib_x = round(3.8 + (hour * 0.14) + (0.3 if hour > 14 else 0.0), 2)
        vib_y = round(3.5 + (hour * 0.12), 2)
        thrust_temp = round(74.0 + (hour * 0.85), 1)
        lube_dp = round(max(0.70, 1.45 - (hour * 0.03)), 2)
        telemetry_rows_02.append({
            "Timestamp": str(base_time + pd.Timedelta(hours=hour)),
            "Asset_Tag": "MRPL-COMP-201-A",
            "Speed_RPM": 8420,
            "Vib_Radial_X_mms": vib_x,
            "Vib_Radial_Y_mms": vib_y,
            "Thrust_Bearing_Temp_C": thrust_temp,
            "Lube_Oil_DP_bar": lube_dp,
            "N2_Seal_Flow_Nm3h": round(10.2 + (hour * 0.35), 1),
            "Alarm_Flag": "CRITICAL" if vib_x > 6.0 or thrust_temp > 90 else ("WARNING" if vib_x > 4.5 else "NORMAL")
        })
    
    with pd.ExcelWriter(tb_dir / "maintenance_history_02.xlsx") as writer:
        pd.DataFrame(maint_rows_02).to_excel(writer, sheet_name="Intervention_History", index=False)
        pd.DataFrame(telemetry_rows_02).to_excel(writer, sheet_name="Sensor_Telemetry", index=False)
    print("Created: maintenance_history_02.xlsx")

    # Image: pump_image_02.jpg
    img2 = Image.new("RGB", (650, 420), color=(20, 25, 38))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([20, 20, 630, 400], outline=(80, 140, 180), width=2)
    d2.rectangle([40, 35, 610, 75], fill=(30, 45, 65))
    d2.text((50, 48), "MRPL VDU-2 WET GAS CENTRIFUGAL COMPRESSOR (MRPL-COMP-201-A)", fill=(240, 245, 255))
    
    # Compressor rotor casing outline
    d2.rectangle([80, 130, 380, 330], fill=(45, 55, 75), outline=(150, 180, 210), width=2)
    # Impeller stages
    for idx, stage_x in enumerate([130, 190, 250, 310]):
        d2.rectangle([stage_x, 150, stage_x + 35, 310], fill=(60, 75, 100), outline=(200, 210, 230))
        d2.text((stage_x + 5, 220), f"S{idx+1}", fill=(255, 255, 255))
    
    # Thrust bearing hotspot box
    d2.rectangle([395, 170, 485, 290], fill=(120, 40, 40), outline=(255, 50, 50), width=3)
    d2.text((400, 180), "THRUST\nBEARING\n94 deg C\nALARM!", fill=(255, 200, 200))
    
    # Orbit plot / FFT vibration graphic
    d2.rectangle([500, 110, 615, 230], fill=(15, 20, 30), outline=(100, 255, 100))
    d2.text((505, 115), "ORBIT PROBE X/Y", fill=(100, 255, 100))
    # Draw elliptical unstable orbit
    d2.ellipse([515, 135, 600, 215], outline=(255, 80, 80), width=2)
    d2.text((515, 235), "Vib: 6.8 mm/s", fill=(255, 100, 100))
    
    draw_gauge(d2, (555, 325), 45, 94, 0, 120, "Thrust T", "C")
    d2.text((80, 355), "ANOMALY: High Radial Vibration (6.8 mm/s) & Hydrodynamic Whirl", fill=(255, 120, 120))
    img2.save(img_dir / "pump_image_02.jpg", quality=92)
    print("Created: pump_image_02.jpg")

    # -------------------------------------------------------------------------
    # ASSET 03: CDU CRUDE PRE-HEAT SHELL-AND-TUBE HEAT EXCHANGER (MRPL-HEX-105-AB)
    # -------------------------------------------------------------------------
    # Document: pump_inspection_03.pdf
    write_pdf(docs_dir / "pump_inspection_03.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "STATIONARY EQUIPMENT INTEGRITY REPORT - CDU PRE-HEAT TRAIN",
        "=======================================================================",
        "Equipment ID: MRPL-HEX-105-AB",
        "Equipment Description: Crude vs Atmospheric Residue Pre-Heat Exchanger",
        "Operating Unit: CDU-1 Pre-Heat Train (Train B)",
        "Inspection Date: 2026-09-04",
        "Inspector: M. V. Chacko (Senior Static Equipment Inspector, API 510/653)",
        "",
        "OBSERVATIONS & THERMAL HYDRAULIC PERFORMANCE:",
        "- Shell-Side Differential Pressure (Residue Stream): 2.45 bar (Clean Baseline: 0.85 bar).",
        "- Tube-Side Differential Pressure (Crude Feed): 1.95 bar (Clean Baseline: 0.90 bar).",
        "- Heat Transfer Coefficient (U-Value): Dropped from design 420 W/m2-K to 215 W/m2-K (48% drop).",
        "- Logarithmic Mean Temperature Difference (LMTD): Severely pinched at 16.2 deg C.",
        "- Ultrasonic Thickness Gauging (UT): Shell wall thickness 14.2 mm (Min retirement: 11.5 mm).",
        "- Gasket Sealing Zone: Channel head flange weeping observed at south nozzle connection.",
        "",
        "SEVERITY & ROOT CAUSE ASSESSMENT:",
        "Severe asphaltene precipitation and heavy coking in tube bundle passes due to desalter",
        "temperature excursion two weeks prior. Excessive hydraulic resistance threatens crude throughput.",
        "",
        "RECOMMENDED CORRECTIVE ACTION PLAN:",
        "1. Isolate Exchanger Train B using block valves and divert through bypass loop.",
        "2. Perform on-line high-pressure hydro-jetting (1200 bar water lancing) of tube bundle.",
        "3. Conduct chemical solvent circulation (aromatic gas oil wash) to dissolve asphaltene matrix.",
        "4. Replace Channel Head Kammprofile metallic gasket before post-cleaning hydrotest."
    ])

    # Knowledge Base: maintenance_sop_03.pdf
    write_pdf(kb_dir / "maintenance_sop_03.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "MAINTENANCE SOP: SHELL & TUBE HEAT EXCHANGER INTEGRITY (SOP-MRPL-HEX-308)",
        "Document Version: 3.2 | Standard: TEMA Class R / API 660 | Custodian: Static Inspection",
        "=======================================================================",
        "SECTION 1: HYDRAULIC & FOULING OPERATIONAL THRESHOLDS",
        "1.1 Pressure Drop (Delta-P) Limits:",
        "    - Clean Baseline Shell Delta-P: 0.70 - 0.90 bar.",
        "    - Advisory Alert Threshold: Delta-P > 1.50 bar (Plan off-line hydro-jetting).",
        "    - Critical Fouling Limit: Delta-P > 2.20 bar (Mandatory bypass diversion within 72 hrs).",
        "",
        "SECTION 2: THERMAL DEGRADATION THRESHOLDS",
        "2.1 Overall Heat Transfer Coefficient Degradation (U/U_design):",
        "    - Acceptable: > 75% of design duty.",
        "    - Marginal / Clean Scheduling Required: 60% to 75%.",
        "    - Severe Degradation / Unacceptable Loss: < 55% of design heat transfer.",
        "",
        "SECTION 3: HYDROSTATIC PRESSURE TESTING & LEAK DETECTION",
        "3.1 Shell-Side Test Pressure: 1.5 x Design Pressure = 37.5 bar gauge.",
        "3.2 Tube-Side Test Pressure: 1.5 x Design Pressure = 28.0 bar gauge.",
        "3.3 Holding Time: Minimum 60 minutes with zero observable pressure decay.",
        "3.4 Tube Plugging Limit: Maximum allowable plugged tubes is 10% of total count (42 tubes).",
        "",
        "SECTION 4: CHEMICAL CLEANING SAFETY PROTOCOL",
        "4.1 Ensure full gas freeing and LEL < 0% before opening channel head cover.",
        "4.2 Neutralize acidic residues with 2% sodium carbonate wash prior to water lance entry."
    ])

    # Table: maintenance_history_03.xlsx
    maint_rows_03 = [
        {"Record_ID": "HEX-2024-03", "Date": "2024-11-12", "Asset_Tag": "MRPL-HEX-105-AB", "Intervention": "Hydro-Jet Tube Cleaning & Gasket Swap", "P_Drop_Before_bar": 2.30, "P_Drop_After_bar": 0.85, "U_Val_Post": 410, "Technician": "K. Nambiar"},
        {"Record_ID": "HEX-2025-01", "Date": "2025-05-18", "Asset_Tag": "MRPL-HEX-105-AB", "Intervention": "Eddy Current Non-Destructive Testing (NDT)", "P_Drop_Before_bar": 1.20, "P_Drop_After_bar": 1.20, "U_Val_Post": 375, "Technician": "S. Rao"},
        {"Record_ID": "HEX-2025-09", "Date": "2025-12-05", "Asset_Tag": "MRPL-HEX-105-AB", "Intervention": "Tube Plugged (Tubes #18, #19)", "P_Drop_Before_bar": 1.45, "P_Drop_After_bar": 1.40, "U_Val_Post": 350, "Technician": "P. Joshi"},
        {"Record_ID": "HEX-2026-04", "Date": "2026-05-20", "Asset_Tag": "MRPL-HEX-105-AB", "Intervention": "Chemical Flush (Solvent Wash)", "P_Drop_Before_bar": 1.95, "P_Drop_After_bar": 1.10, "U_Val_Post": 340, "Technician": "K. Nambiar"},
    ]
    # Telemetry logging daily fouling progression
    telemetry_rows_03 = []
    base_date = pd.Timestamp("2026-08-10")
    for day in range(30):
        t_crude_in = 135.0
        t_crude_out = round(210.0 - (day * 1.1), 1)
        dp_shell = round(1.10 + (day * 0.046), 2)
        dp_tube = round(0.95 + (day * 0.033), 2)
        u_val = round(340.0 - (day * 4.2), 1)
        telemetry_rows_03.append({
            "Date": str((base_date + pd.Timedelta(days=day)).date()),
            "Asset_Tag": "MRPL-HEX-105-AB",
            "Crude_Inlet_Temp_C": t_crude_in,
            "Crude_Outlet_Temp_C": t_crude_out,
            "Residue_Inlet_Temp_C": 315.0,
            "Residue_Outlet_Temp_C": round(235.0 + (day * 0.9), 1),
            "Shell_DeltaP_bar": dp_shell,
            "Tube_DeltaP_bar": dp_tube,
            "Heat_Transfer_Coeff_U": u_val,
            "Fouling_Status": "CRITICAL" if dp_shell > 2.2 else ("WARNING" if dp_shell > 1.5 else "NORMAL")
        })

    with pd.ExcelWriter(tb_dir / "maintenance_history_03.xlsx") as writer:
        pd.DataFrame(maint_rows_03).to_excel(writer, sheet_name="Cleaning_History", index=False)
        pd.DataFrame(telemetry_rows_03).to_excel(writer, sheet_name="Thermal_Telemetry", index=False)
    print("Created: maintenance_history_03.xlsx")

    # Image: pump_image_03.jpg
    img3 = Image.new("RGB", (650, 420), color=(15, 20, 30))
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([20, 20, 630, 400], outline=(200, 140, 60), width=2)
    d3.rectangle([40, 35, 610, 75], fill=(45, 30, 20))
    d3.text((50, 48), "MRPL CDU-1 CRUDE PRE-HEAT EXCHANGER IR THERMAL SCAN (MRPL-HEX-105-AB)", fill=(255, 230, 180))
    
    # Exchanger cylinder shell
    d3.rectangle([70, 140, 520, 320], fill=(50, 50, 60), outline=(180, 180, 190), width=3)
    # Heatmap color gradient across shell (left hot to right cold with blocked tubes)
    for seg_idx, x_pos in enumerate(range(85, 505, 30)):
        # Color transition representing temperature drop & fouling blockage
        r_col = int(max(40, 255 - seg_idx * 15))
        b_col = int(min(220, 40 + seg_idx * 16))
        g_col = int(80 + (40 if seg_idx % 2 == 0 else 0))
        d3.rectangle([x_pos, 155, x_pos + 26, 305], fill=(r_col, g_col, b_col))
    
    # Channel head & tube sheet callouts
    d3.rectangle([70, 140, 110, 320], fill=(70, 70, 80), outline=(255, 60, 60), width=2)
    d3.text((80, 210), "TUBE\nSHEET", fill=(255, 255, 255))
    
    # Text overlays
    d3.rectangle([340, 170, 500, 280], fill=(20, 25, 35), outline=(255, 120, 40), width=2)
    d3.text((350, 180), "THERMAL ANOMALY:\nShell DeltaP: 2.45 bar\n(Limit: 1.50 bar)\nU-Drop: -48%\nSevere Coking Zone", fill=(255, 200, 100))
    
    draw_gauge(d3, (575, 230), 42, 2.45, 0.0, 3.5, "Delta-P", "bar")
    img3.save(img_dir / "pump_image_03.jpg", quality=92)
    print("Created: pump_image_03.jpg")

    # -------------------------------------------------------------------------
    # ASSET 04: CDU ATMOSPHERIC DISTILLATION COLUMN (MRPL-COL-301)
    # -------------------------------------------------------------------------
    # Document: pump_inspection_04.pdf
    write_pdf(docs_dir / "pump_inspection_04.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "PROCESS VESSEL COLUMN INTEGRITY & GAMMA SCAN REPORT - CDU-1",
        "=======================================================================",
        "Equipment ID: MRPL-COL-301",
        "Equipment Description: Main Atmospheric Crude Distillation Column",
        "Operating Unit: Crude Distillation Unit 1 (Capacity 12.0 MMTPA)",
        "Inspection Date: 2026-09-06",
        "Radiometric Inspection Contractor: Tracerco Industrial Radiometrics Ltd.",
        "",
        "HYDRAULIC & RADIOMETRIC SCAN SUMMARY (TRAYS 15 TO 32):",
        "- Total Column Differential Pressure (Top to Bottom): 0.78 bar (SOP Maximum: 0.65 bar).",
        "- Tray 20 to 24 Differential Pressure: 0.38 bar (High liquid hold-up / flooding).",
        "- Gamma Radiometric Density Scan: Detected severe aerated liquid backup on Trays 21-22.",
        "- Kerosene/Diesel Fractionation Cut: ASTM D86 95% boiling point overlap widened by 22 deg C.",
        "- Column Top Temperature: 134 deg C (Design Operating Window: 110 - 122 deg C).",
        "- Reflux Accumulator Level: Surging between 35% and 88% with heavy entrainment.",
        "",
        "DIAGNOSIS & ROOT CAUSE:",
        "Localized downcomer choking and tray damage around wash zone (Trays 21-23) triggered by",
        "sudden water flashing from crude feed tank bottom settling failure.",
        "",
        "MAINTENANCE RECOMMENDATION & MITIGATION:",
        "1. Immediate adjustment of pumparound duty (+15%) to de-inventory middle wash section.",
        "2. Reduce crude furnace outlet temperature by 4 deg C to reduce vapor superficial velocity.",
        "3. Schedule mini-turnaround internal entry to replace collapsed valve trays (Trays 21-23).",
        "4. Inspect chimney tray seals and downcomer bolting with austenitic SS 316L hardware."
    ])

    # Knowledge Base: maintenance_sop_04.pdf
    write_pdf(kb_dir / "maintenance_sop_04.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "OPERATING MANUAL & SOP: CRUDE DISTILLATION COLUMN (SOP-MRPL-DIST-602)",
        "Document Version: 3.5 | Engineering Discipline: Process & Vessel Inspection",
        "=======================================================================",
        "SECTION 1: HYDRAULIC STABILITY LIMITS & FLOODING CRITERIA",
        "1.1 Allowable Differential Pressure Profile:",
        "    - Overall Column Differential Pressure (Bottom - Overhead): <= 0.65 bar.",
        "    - Single Tray Differential Pressure: 8.0 to 14.0 mbar (0.008 to 0.014 bar).",
        "    - Jet Flooding Margin: Operating vapor velocity must not exceed 82% of flooding velocity.",
        "",
        "SECTION 2: TEMPERATURE & TOP PRODUCT CONTROL WINDOW",
        "2.1 Overhead Vapor Temperature: 112 deg C to 122 deg C. High Alarm: 128 deg C.",
        "2.2 Top Flash Pressure: 1.45 to 1.65 bar absolute.",
        "2.3 Flash Zone Operating Temperature: 360 deg C to 368 deg C.",
        "",
        "SECTION 3: WEAPONS AGAINST FOULING, WEAPING & CORROSION",
        "3.1 Desalted Crude Salt Content Limit: Maximum 3.0 PTB (Pounds per Thousand Barrels).",
        "3.2 Overhead Overhead pH: Maintain neutralizer injection to sustain water condensate pH 6.0 - 6.8.",
        "3.3 Downcomer Clearances: Minimum downcomer clearance of 38 mm on heavy wash trays.",
        "",
        "SECTION 4: EMERGENCY MITIGATION PROTOCOL",
        "Condition: Column DP > 0.75 bar + Liquid Carryover.",
        "Immediate Action: Reduce stripping steam flow by 20%, increase heavy naphtha reflux."
    ])

    # Table: maintenance_history_04.xlsx
    maint_rows_04 = [
        {"Turnaround_ID": "TA-2023-CDU1", "Date": "2023-04-10", "Asset_Tag": "MRPL-COL-301", "Section": "Flash Zone & Wash Trays", "Scope": "Replaced Trays 18-24 with Structured Packing", "Inspector": "N. Deshmukh", "Duration_Days": 18, "Status": "Completed"},
        {"Turnaround_ID": "MNT-2024-08", "Date": "2024-08-22", "Asset_Tag": "MRPL-COL-301", "Section": "Overhead Condenser Nozzles", "Scope": "Ultrasonic Flange Face Inspection", "Inspector": "B. Hegde", "Duration_Days": 2, "Status": "Completed"},
        {"Turnaround_ID": "MNT-2025-05", "Date": "2025-05-14", "Asset_Tag": "MRPL-COL-301", "Section": "Overhead Neutralizer Quench", "Scope": "Corrosion Probe & Quench Quill Replacement", "Inspector": "S. Rao", "Duration_Days": 1, "Status": "Completed"},
        {"Turnaround_ID": "MNT-2026-03", "Date": "2026-03-30", "Asset_Tag": "MRPL-COL-301", "Section": "Chimney Tray 14", "Scope": "Downcomer Bolting Inspection & Cleanout", "Inspector": "N. Deshmukh", "Duration_Days": 3, "Status": "Completed"},
    ]
    # Telemetry data recording column pressure profile across trays
    telemetry_rows_04 = []
    base_time = pd.Timestamp("2026-09-06 00:00:00")
    for step in range(24):
        total_dp = round(0.55 + (step * 0.011), 3)
        wash_dp = round(0.18 + (step * 0.009), 3)
        top_temp = round(118.0 + (step * 0.7), 1)
        telemetry_rows_04.append({
            "Timestamp": str(base_time + pd.Timedelta(hours=step)),
            "Asset_Tag": "MRPL-COL-301",
            "Crude_Charge_Rate_m3h": round(1420 - step * 5, 0),
            "Column_Total_DeltaP_bar": total_dp,
            "Wash_Trays_20_24_DeltaP_bar": wash_dp,
            "Overhead_Vapor_Temp_C": top_temp,
            "Flash_Zone_Temp_C": 365.2,
            "Reflux_Flow_m3h": round(310 + step * 2.5, 1),
            "Salt_PTB": round(2.8 + step * 0.08, 2),
            "Hydraulic_State": "FLOODING" if total_dp > 0.72 else ("ALERT" if total_dp > 0.65 else "NORMAL")
        })

    with pd.ExcelWriter(tb_dir / "maintenance_history_04.xlsx") as writer:
        pd.DataFrame(maint_rows_04).to_excel(writer, sheet_name="Turnaround_Records", index=False)
        pd.DataFrame(telemetry_rows_04).to_excel(writer, sheet_name="Hydraulic_Telemetry", index=False)
    print("Created: maintenance_history_04.xlsx")

    # Image: pump_image_04.jpg
    img4 = Image.new("RGB", (650, 420), color=(18, 24, 34))
    d4 = ImageDraw.Draw(img4)
    d4.rectangle([20, 20, 630, 400], outline=(120, 160, 200), width=2)
    d4.rectangle([40, 35, 610, 75], fill=(30, 40, 55))
    d4.text((50, 48), "MRPL CDU-1 MAIN DISTILLATION COLUMN HYDRAULICS (MRPL-COL-301)", fill=(240, 245, 255))
    
    # Column vertical tower graphic
    d4.rectangle([100, 100, 230, 380], fill=(40, 50, 65), outline=(200, 210, 220), width=3)
    # Trays with downcomers
    for tray_idx, tray_y in enumerate(range(120, 370, 22)):
        is_flooded = 180 <= tray_y <= 240
        fill_col = (230, 70, 70) if is_flooded else (100, 120, 145)
        d4.line([(105, tray_y), (225, tray_y)], fill=fill_col, width=3 if is_flooded else 2)
        if is_flooded:
            d4.rectangle([110, tray_y - 8, 220, tray_y], fill=(180, 50, 50))
    
    d4.text((250, 140), "OVERHEAD VAPOR: 134 deg C (HIGH)", fill=(255, 180, 100))
    d4.rectangle([250, 180, 480, 270], fill=(30, 35, 45), outline=(255, 70, 70), width=2)
    d4.text((260, 190), "GAMMA SCAN OBSERVATION:\nTrays 20-24 Flooding Detected\nLiquid Backup in Downcomers\nDelta-P: 0.78 bar (Limit: 0.65)", fill=(255, 150, 150))
    
    draw_gauge(d4, (555, 230), 45, 0.78, 0.2, 1.0, "Col DP", "bar")
    img4.save(img_dir / "pump_image_04.jpg", quality=92)
    print("Created: pump_image_04.jpg")

    # -------------------------------------------------------------------------
    # ASSET 05: VDU VACUUM BOTTOMS SEVERE SERVICE CONTROL VALVE (MRPL-VALVE-402-MOV)
    # -------------------------------------------------------------------------
    # Document: pump_inspection_05.pdf
    write_pdf(docs_dir / "pump_inspection_05.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "SEVERE SERVICE VALVE DIAGNOSTIC INSPECTION - VDU VACUUM SECTION",
        "=======================================================================",
        "Equipment ID: MRPL-VALVE-402-MOV",
        "Equipment Description: Vacuum Tower Bottoms Emergency Isolation & Letdown Valve",
        "Operating Unit: VDU-1 Vacuum Residue Transfer System",
        "Inspection Date: 2026-09-07",
        "Inspector: D. Fernandez (Control Valves & Actuation Reliability Team)",
        "",
        "FIELD DIAGNOSTIC OBSERVATIONS & SIGNATURE ANALYSIS:",
        "- Actuator Motor Running Torque Margin: Dropped to 14% (Minimum required safety margin: 30%).",
        "- Valve Full Stroke Time (Closed to Open): 48.5 seconds (Allowable limit: <= 25.0 seconds).",
        "- Acoustic Emission Sensor (AE): Ultrasonic noise 84 dB at 38 kHz (Severe cavitation erosion).",
        "- Stem Packing Gland Zone: Severe graphite packing extrusion with active pitch tar weeping.",
        "- Seat Leakage (FCI 70-2 Class VI Test): Passing 4.2 L/min against zero-leakage requirement.",
        "- Internal Trim Condition: Stellite-faced plug and cage exhibit micro-pitting and washouts.",
        "",
        "SAFETY & COMPLIANCE EVALUATION: LEVEL 2 HIGH ALERT",
        "Sluggish emergency closure and seat leakage under 380 deg C vacuum residue service risks fire",
        "hazard upon downstream transfer line isolation during emergency unit de-pressurization.",
        "",
        "ACTION DIRECTIVE:",
        "1. Re-torque actuator bevel gearbox packing bolts immediately to restore temporary seal.",
        "2. Prepare spare tungsten carbide cage trim assembly (Type 410 / Satellite 6).",
        "3. Schedule isolation valve hot-swap during upcoming planned maintenance window.",
        "4. Overhaul Limitorque electric actuator gearbox and replace degraded worm drive bearings."
    ])

    # Knowledge Base: maintenance_sop_05.pdf
    write_pdf(kb_dir / "maintenance_sop_05.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "STANDARD OPERATING PROCEDURE: SEVERE SERVICE CONTROL VALVES (SOP-MRPL-INST-204)",
        "Document Version: 2.8 | Standards: ANSI/FCI 70-2 / ISA-75.01 | Custodian: Instrumentation",
        "=======================================================================",
        "SECTION 1: ACTUATOR TORQUE MARGINS & TIMING CRITERIA",
        "1.1 Motor-Operated Valve (MOV) Torque Margin:",
        "    - Required Available Torque Margin: >= 30% above unseating breakaway torque.",
        "    - Warning Threshold: Torque margin between 20% and 29%.",
        "    - Critical Threshold: Margin < 20% requires immediate actuator overhaul.",
        "1.2 Full Stroke Time Tolerance:",
        "    - Emergency Isolation Valves: Must fully close within 25.0 seconds.",
        "    - Stroke time exceeding 30 seconds triggers safety loop compliance violation.",
        "",
        "SECTION 2: SEAT LEAKAGE & ACOUSTIC CAVITATION STANDARDS",
        "2.1 Class VI Shut-Off Criteria: Zero visible bubble leakage at ambient test conditions.",
        "2.2 Acoustic Cavitation Thresholds (Ultrasonic 30 - 45 kHz band):",
        "    - Normal Non-Cavitating Operation: < 55 dB.",
        "    - Mild Incipient Cavitation: 55 to 68 dB.",
        "    - Severe Cavitation / Trim Erosion Risk: > 72 dB.",
        "",
        "SECTION 3: PACKING GLAND & HIGH-TEMPERATURE RESIDUE SERVICE",
        "3.1 Gland Packing Material: High-purity flexible graphite with Inconel wire reinforcement.",
        "3.2 Live-Loaded Belleville Springs: Check spring deflection every 6 months to maintain load."
    ])

    # Table: maintenance_history_05.xlsx
    maint_rows_05 = [
        {"Ticket_ID": "VALV-2024-11", "Date": "2024-10-15", "Asset_Tag": "MRPL-VALVE-402-MOV", "Intervention": "Packing Replacement & Stellite Trim Inspection", "Technician": "D. Fernandez", "Stroke_Time_s": 21.2, "Torque_Margin_Pct": 42, "Status": "Passed"},
        {"Ticket_ID": "VALV-2025-04", "Date": "2025-03-20", "Asset_Tag": "MRPL-VALVE-402-MOV", "Intervention": "Actuator Limit Switch Calibration", "Technician": "R. Shenoy", "Stroke_Time_s": 22.0, "Torque_Margin_Pct": 38, "Status": "Passed"},
        {"Ticket_ID": "VALV-2025-11", "Date": "2025-11-10", "Asset_Tag": "MRPL-VALVE-402-MOV", "Intervention": "Gland Nut Tightening & Grease Injection", "Technician": "D. Fernandez", "Stroke_Time_s": 26.5, "Torque_Margin_Pct": 28, "Status": "Passed"},
        {"Ticket_ID": "VALV-2026-06", "Date": "2026-06-18", "Asset_Tag": "MRPL-VALVE-402-MOV", "Intervention": "Ultrasonic Leak Diagnostic & Signature Test", "Technician": "D. Fernandez", "Stroke_Time_s": 36.2, "Torque_Margin_Pct": 21, "Status": "Warning"},
    ]
    # Telemetry data recording diagnostic stroke tests and acoustic dB
    telemetry_rows_05 = []
    base_time = pd.Timestamp("2026-09-07 00:00:00")
    for hr in range(24):
        torque_margin = round(max(12.0, 24.0 - (hr * 0.45)), 1)
        stroke_t = round(min(50.0, 32.0 + (hr * 0.72)), 1)
        acoustic_db = round(min(88.0, 68.0 + (hr * 0.68)), 1)
        telemetry_rows_05.append({
            "Timestamp": str(base_time + pd.Timedelta(hours=hr)),
            "Asset_Tag": "MRPL-VALVE-402-MOV",
            "Valve_Position_Pct": 45.0,
            "Torque_Margin_Pct": torque_margin,
            "Stroke_Time_Seconds": stroke_t,
            "Acoustic_Noise_dB": acoustic_db,
            "Packing_Box_Temp_C": round(185.0 + hr * 1.2, 1),
            "Leak_Rate_Lmin": round(0.5 + hr * 0.15, 2),
            "Operational_Health": "CRITICAL" if torque_margin < 20 or stroke_t > 35 else "WARNING"
        })

    with pd.ExcelWriter(tb_dir / "maintenance_history_05.xlsx") as writer:
        pd.DataFrame(maint_rows_05).to_excel(writer, sheet_name="Maintenance_Logs", index=False)
        pd.DataFrame(telemetry_rows_05).to_excel(writer, sheet_name="Signature_Telemetry", index=False)
    print("Created: maintenance_history_05.xlsx")

    # Image: pump_image_05.jpg
    img5 = Image.new("RGB", (650, 420), color=(22, 28, 38))
    d5 = ImageDraw.Draw(img5)
    d5.rectangle([20, 20, 630, 400], outline=(150, 130, 90), width=2)
    d5.rectangle([40, 35, 610, 75], fill=(45, 40, 30))
    d5.text((50, 48), "MRPL VDU VACUUM BOTTOMS ISOLATION VALVE (MRPL-VALVE-402-MOV)", fill=(245, 235, 210))
    
    # Valve body outline
    d5.polygon([(120, 250), (220, 200), (220, 300)], fill=(70, 75, 85), outline=(200, 210, 220))
    d5.polygon([(320, 250), (220, 200), (220, 300)], fill=(70, 75, 85), outline=(200, 210, 220))
    # Actuator on top
    d5.rectangle([190, 110, 250, 200], fill=(80, 50, 50), outline=(255, 80, 80), width=2)
    d5.ellipse([175, 90, 265, 120], fill=(100, 60, 60), outline=(255, 100, 100))
    d5.text((185, 135), "ACTUATOR\nTORQUE\nMARGIN:\n14% (LOW)", fill=(255, 200, 200))
    
    # Acoustic Cavitation Heatmap
    d5.rectangle([340, 140, 510, 270], fill=(25, 30, 40), outline=(255, 150, 50), width=2)
    d5.text((350, 150), "ULTRASONIC ACOUSTIC SCAN:\nNoise Level: 84 dB @ 38kHz\nClass VI Seat Leakage: 4.2 L/m\nStroke Time: 48.5 s (Limit: 25s)\nStatus: Severe Cavitation Erosion", fill=(255, 190, 120))
    
    draw_gauge(d5, (565, 215), 45, 84, 30, 100, "Acoustic", "dB")
    draw_gauge(d5, (565, 335), 45, 48.5, 0, 60, "Stroke", "sec")
    img5.save(img_dir / "pump_image_05.jpg", quality=92)
    print("Created: pump_image_05.jpg")

    # -------------------------------------------------------------------------
    # ASSET 06: CDU FIRED HEATER RADIANT TUBE SUPERHEATER (MRPL-BOIL-501-HP)
    # -------------------------------------------------------------------------
    # Document: pump_inspection_06.pdf
    write_pdf(docs_dir / "pump_inspection_06.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "FIRED HEATER RADIANT COIL INFRARED THERMOGRAPHY INSPECTION - CDU-1",
        "=======================================================================",
        "Equipment ID: MRPL-BOIL-501-HP",
        "Equipment Description: Atmospheric Crude Fired Heater & Radiant Steam Coil",
        "Operating Unit: CDU-1 Crude Charge Furnace Section",
        "Inspection Date: 2026-09-09",
        "Thermographer: K. R. Nagesh (Level III Certified Infrared Thermographer)",
        "",
        "THERMAL IMAGING & TUBE INTEGRITY FINDINGS:",
        "- Radiant Tube Skin Thermocouple (TI-501-14, South Wall): 722 deg C (Design Limit: 650 deg C).",
        "- Adjacent Skin Thermocouple (TI-501-15): 708 deg C.",
        "- IR Camera Radiometric Hotspot Band: Localized thermal banding 1.8 meters in length on Coil #4.",
        "- Flame Impingement Observation: Burner #6 tile degraded causing direct flame impingement on tubes.",
        "- Draft Pressure at Arch: -1.2 mm H2O (Recommended range: -2.5 to -4.0 mm H2O).",
        "- Tube Sagging & Bowing: Visual laser alignment reveals 28 mm horizontal tube sag on Pass 2.",
        "",
        "METALLURGICAL RISK RATING: EXTREME / HIGH PRIORITY",
        "Operating 9% Cr-1 Mo radiant tubes above 700 deg C accelerates creep rupture and severe",
        "internal coking, presenting an imminent furnace tube rupture hazard.",
        "",
        "URGENT OPERATIONAL RECOMMENDATIONS:",
        "1. Immediately throttle fuel gas to Burner #6 and bias firing load to east wall burners.",
        "2. Increase steam-to-oil decoking ratio by 10% to enhance internal convective heat removal.",
        "3. Adjust stack damper to restore firebox draft to -3.0 mm H2O to eliminate positive arch pressure.",
        "4. Plan pigging / online steam-air decoking of Radiant Pass 2 during upcoming maintenance."
    ])

    # Knowledge Base: maintenance_sop_06.pdf
    write_pdf(kb_dir / "maintenance_sop_06.pdf", [
        "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)",
        "OPERATING STANDARD: FIRED HEATER TUBE MANAGEMENT & DECOKING (SOP-MRPL-HEAT-710)",
        "Document Version: 4.1 | Standard: API 530 / API 560 | Custodian: Furnace Reliability",
        "=======================================================================",
        "SECTION 1: TUBE SKIN TEMPERATURE LIMITS & CREEP PRESERVATION",
        "1.1 Maximum Allowable Tube Skin Temperatures (API 530 Design Margins):",
        "    - Carbon Steel (A106-B): Max 454 deg C.",
        "    - 5% Cr - 0.5% Mo (ASTM A335 P5): Max 593 deg C.",
        "    - 9% Cr - 1% Mo (ASTM A335 P9): Normal limit 650 deg C. Emergency Alarm at 685 deg C.",
        "    - Operation above 700 deg C drastically reduces creep life by 90% per 15 deg C increment.",
        "",
        "SECTION 2: FIREBOX DRAFT & COMBUSTION CONTROL",
        "2.1 Arch Draft: Must strictly be maintained negative between -2.0 and -5.0 mm H2O.",
        "2.2 Excess O2 Target: 2.5% to 3.5% at arch. High O2 accelerates outer tube scale formation.",
        "",
        "SECTION 3: STEAM-AIR DECOKING CRITERIA & PIGGING",
        "3.1 Tube Decoking Trigger: When clean tube skin vs process fluid temperature Delta-T > 95 deg C.",
        "3.2 Mechanical Decoking (Pigging): Required when pressure drop across radiant pass increases > 35%.",
        "3.3 Spalling Verification: Monitor effluent quench water until zero carbon fines are observed."
    ])

    # Image: pump_image_06.jpg
    img6 = Image.new("RGB", (650, 420), color=(25, 20, 20))
    d6 = ImageDraw.Draw(img6)
    d6.rectangle([20, 20, 630, 400], outline=(220, 100, 50), width=2)
    d6.rectangle([40, 35, 610, 75], fill=(55, 30, 25))
    d6.text((50, 48), "MRPL CDU-1 FIRED HEATER RADIANT TUBE THERMAL SCAN (MRPL-BOIL-501-HP)", fill=(255, 230, 210))
    
    # Firebox radiant tubes outline
    d6.rectangle([70, 130, 520, 330], fill=(35, 30, 35), outline=(150, 100, 80), width=2)
    # Vertical / horizontal radiant tube coils
    for coil_idx, y_coil in enumerate(range(150, 310, 30)):
        is_hotspot = coil_idx in [1, 2]
        coil_col = (255, 50, 50) if is_hotspot else (200, 140, 70)
        d6.line([(90, y_coil), (500, y_coil)], fill=coil_col, width=8 if is_hotspot else 5)
        if is_hotspot:
            # Hotspot thermal flare
            d6.ellipse([240, y_coil - 12, 380, y_coil + 12], fill=(255, 240, 100), outline=(255, 80, 20))
    
    d6.rectangle([110, 250, 360, 320], fill=(20, 20, 25), outline=(255, 80, 80), width=2)
    d6.text((120, 255), "INFRARED HOTSPOT BAND (PASS 2):\nMeasured Tube Skin: 722 deg C\nDesign Limit (API 530): 650 deg C\nCause: Burner Impingement & Coking", fill=(255, 220, 120))
    
    draw_gauge(d6, (565, 230), 45, 722, 400, 850, "Skin Temp", "C")
    img6.save(img_dir / "pump_image_06.jpg", quality=92)
    print("Created: pump_image_06.jpg")

    print("\n[SUCCESS]: All 19 new synthetic demo files and baseline files created successfully!")
    print(f"- documents/      : {len(list(docs_dir.glob('*.pdf')))} PDF files")
    print(f"- images/         : {len(list(img_dir.glob('*.jpg')))} JPG files")
    print(f"- knowledge_base/ : {len(list(kb_dir.glob('*.pdf')))} PDF files")
    print(f"- tables/         : {len(list(tb_dir.glob('*.xlsx')))} XLSX files")

if __name__ == "__main__":
    create_synthetic_demo_files()
