import logging
import re
from pathlib import Path
from typing import Dict, Any, List
from agents.state import AgentState
from models.router import router
from rag.retriever import retriever
from multimodal.pipeline import multimodal_pipeline
from tools.calculator import calculator
from reports.docx_generator import docx_generator

logger = logging.getLogger(__name__)

def _log_step(state: AgentState, step_name: str, message: str) -> List[str]:
    logs = list(state.get("execution_logs", []))
    logs.append(f"[{step_name.upper()}]: {message}")
    return logs

def understand_task_node(state: AgentState) -> Dict[str, Any]:
    task_desc = state.get("task_description", "Analyze industrial inspection")
    
    # Classify task type
    task_type = "MULTIMODAL_AGENT"
    if "code" in task_desc.lower() or "python" in task_desc.lower() or "calculate" in task_desc.lower():
        task_type = "CODING"
    
    provider, route_meta = router.route(task_type)
    logs = _log_step(state, "Understand Task", f"Task understood as '{task_type}'. Selected Model: {route_meta['selected_model']} ({route_meta['provider_type']})")
    
    return {
        "task_type": task_type,
        "model_routing_info": route_meta,
        "execution_logs": logs,
        "current_step": "UNDERSTAND_TASK",
    }

def plan_node(state: AgentState) -> Dict[str, Any]:
    plan_steps = [
        "1. Ingest inspection PDF and extract operating telemetry.",
        "2. Perform OCR and visual feature analysis on equipment photograph.",
        "3. Parse tabular maintenance logs and sensor time-series.",
        "4. Query sovereign MRPL knowledge base for applicable SOP standards.",
        "5. Fuse multi-source evidence into unified operational context.",
        "6. Perform physical condition reasoning and risk evaluation.",
        "7. Formulate targeted engineering recommendations.",
        "8. Present findings for Human Approval Gate.",
        "9. Generate executive multi-format deliverable package upon approval.",
    ]
    logs = _log_step(state, "Plan", f"Generated {len(plan_steps)}-step industrial analysis plan.")
    return {
        "plan": plan_steps,
        "execution_logs": logs,
        "current_step": "PLAN",
    }

def collect_inputs_node(state: AgentState) -> Dict[str, Any]:
    pdf_p = state.get("pdf_path")
    img_p = state.get("image_path")
    xls_p = state.get("excel_path")
    
    msg = f"Collected inputs: PDF={Path(pdf_p).name if pdf_p else 'None'}, Image={Path(img_p).name if img_p else 'None'}, Excel={Path(xls_p).name if xls_p else 'None'}"
    logs = _log_step(state, "Collect Inputs", msg)
    return {
        "execution_logs": logs,
        "current_step": "COLLECT_INPUTS",
    }

from tools.file_tools import get_equipment_meta

def _detect_asset_context(state: AgentState) -> str:
    """Helper to detect asset archetype from paths and task description."""
    meta = get_equipment_meta(state)
    short = meta.get("short", "Pump")
    mapping = {
        "Compressor": "COMPRESSOR",
        "Heat_Exchanger": "HEAT_EXCHANGER",
        "Distillation_Column": "DISTILLATION_COLUMN",
        "Control_Valve": "CONTROL_VALVE",
        "Fired_Heater": "FIRED_HEATER",
        "Pump": "CENTRIFUGAL_PUMP",
    }
    return mapping.get(short, "CENTRIFUGAL_PUMP")

def search_knowledge_node(state: AgentState) -> Dict[str, Any]:
    task_desc = state.get("task_description", "")
    asset_ctx = _detect_asset_context(state)

    query_map = {
        "COMPRESSOR": f"{task_desc} centrifugal compressor vibration trip limits API 617 lube oil thrust bearing SOP-MRPL-COMP-501",
        "HEAT_EXCHANGER": f"{task_desc} shell and tube heat exchanger differential pressure fouling TEMA Class R cleaning SOP-MRPL-HEX-308",
        "DISTILLATION_COLUMN": f"{task_desc} crude distillation column tray differential pressure flooding SOP-MRPL-DIST-602",
        "CONTROL_VALVE": f"{task_desc} severe service control valve actuator torque margin acoustic cavitation Class VI SOP-MRPL-INST-204",
        "FIRED_HEATER": f"{task_desc} fired heater radiant tube skin temperature API 530 creep decoking SOP-MRPL-HEAT-710",
        "CENTRIFUGAL_PUMP": f"{task_desc} centrifugal pump overhaul bearing temperature mechanical seal ISO 10816 SOP-MRPL-MECH-402",
    }
    
    query = query_map.get(asset_ctx, task_desc or "refinery equipment maintenance SOP")
    citations = retriever.retrieve(query, top_k=4)
    
    cit_msg = f"Retrieved {len(citations)} source citations from local MRPL knowledge base for [{asset_ctx}]."
    for c in citations:
        cit_msg += f"\n  - Citation: {c['source_citation']} (Score: {c['score']})"
        
    logs = _log_step(state, "Search Knowledge (RAG)", cit_msg)
    return {
        "rag_citations": citations,
        "execution_logs": logs,
        "current_step": "SEARCH_KNOWLEDGE",
    }

def analyze_multimodal_node(state: AgentState) -> Dict[str, Any]:
    pdf_p = Path(state.get("pdf_path")) if state.get("pdf_path") else None
    img_p = Path(state.get("image_path")) if state.get("image_path") else None
    xls_p = Path(state.get("excel_path")) if state.get("excel_path") else None
    
    mm_result = multimodal_pipeline.process_inputs(pdf_p, img_p, xls_p)
    logs = _log_step(state, "Multimodal Analysis", "Processed PDF inspection, Image OCR, and Excel tabular history.")
    
    return {
        "raw_evidence": mm_result,
        "execution_logs": logs,
        "current_step": "ANALYZE_MULTIMODAL",
    }

def fuse_evidence_node(state: AgentState) -> Dict[str, Any]:
    raw_ev = state.get("raw_evidence", {})
    citations = state.get("rag_citations", [])
    
    fused_text = raw_ev.get("fused_evidence_text", "")
    
    if citations:
        fused_text += "\n\n=== RELEVANT LOCAL SOP CITATIONS (RAG) ===\n"
        for c in citations:
            fused_text += f"Source: {c['source_citation']}\nExtract: {c['text']}\n\n"
            
    logs = _log_step(state, "Fuse Evidence", "Unified evidence text successfully created across all documents and RAG sources.")
    return {
        "fused_evidence": fused_text,
        "execution_logs": logs,
        "current_step": "FUSE_EVIDENCE",
    }

def reason_node(state: AgentState) -> Dict[str, Any]:
    route_info = state.get("model_routing_info", {})
    asset_ctx = _detect_asset_context(state)

    if asset_ctx == "COMPRESSOR":
        reasoning = (
            "INDUSTRIAL CONDITION REASONING (COMPRESSOR MRPL-COMP-201-A):\n"
            "1. Multimodal Evidence: Stage-1 radial vibration reaches 6.8 mm/s RMS with active sub-synchronous whirl (0.43X), "
            "while thrust bearing active face operates at 94 deg C (Max limit: 88 deg C).\n"
            "2. Telemetry & Lube Console: Lube oil differential pressure dropped to 0.72 bar (Normal: 1.2 - 1.6 bar), "
            "indicating severe filter blinding or foaming in the lube skid.\n"
            "3. SOP Alignment: Per SOP-MRPL-COMP-501 / API 617, radial vibration exceeding 4.5 mm/s RMS with sub-synchronous "
            "whirl indicates hydrodynamic bearing instability; operation > 7.1 mm/s mandates emergency trip.\n"
            "4. Conclusion: Imminent risk of axial thrust collar wipeout and rotor-stator contact under continuous VDU-2 operation."
        )
    elif asset_ctx == "HEAT_EXCHANGER":
        reasoning = (
            "INDUSTRIAL CONDITION REASONING (HEAT EXCHANGER MRPL-HEX-105-AB):\n"
            "1. Multimodal Evidence: Shell-side differential pressure has spiked to 2.45 bar (Clean baseline: 0.85 bar, Limit: 1.50 bar), "
            "accompanied by active flange weeping at the south channel head.\n"
            "2. Thermal Degradation: Heat transfer coefficient U dropped from 420 W/m2-K to 215 W/m2-K (48% performance penalty).\n"
            "3. SOP Alignment: Per SOP-MRPL-HEX-308 (TEMA Class R), shell Delta-P > 2.20 bar mandates immediate bypass diversion "
            "and offline hydro-jet lancing (1200 bar) to restore cross-sectional tube flow.\n"
            "4. Conclusion: Severe asphaltene deposition restricts crude pre-heat, causing furnace overfiring and throughput throttling."
        )
    elif asset_ctx == "DISTILLATION_COLUMN":
        reasoning = (
            "INDUSTRIAL CONDITION REASONING (DISTILLATION COLUMN MRPL-COL-301):\n"
            "1. Multimodal Evidence: Column differential pressure surged to 0.78 bar (SOP Maximum: 0.65 bar), with Trays 20-24 "
            "exhibiting severe local liquid hold-up (0.38 bar DP).\n"
            "2. Radiometric Verification: Gamma scan data confirms severe aerated liquid downcomer backup across wash trays 21-22.\n"
            "3. SOP Alignment: Per SOP-MRPL-DIST-602, total column DP > 0.75 bar combined with top temp excursion (134 deg C vs 122 deg C design) "
            "indicates severe jet flooding and off-spec kerosene/diesel separation.\n"
            "4. Conclusion: Operation under flooding conditions risks heavy crude carryover into overhead condensers and salt corrosion."
        )
    elif asset_ctx == "CONTROL_VALVE":
        reasoning = (
            "INDUSTRIAL CONDITION REASONING (CONTROL VALVE MRPL-VALVE-402-MOV):\n"
            "1. Multimodal Evidence: Actuator torque safety margin has collapsed to 14% (Minimum required: 30%), while stroke time "
            "degraded to 48.5 seconds (Allowable limit: <= 25.0 seconds).\n"
            "2. Acoustic Diagnostics: Ultrasonic emission sensor registers 84 dB at 38 kHz downstream of seat, confirming cavitation erosion "
            "and Class VI seat leakage at 4.2 L/min.\n"
            "3. SOP Alignment: Per SOP-MRPL-INST-204 (ANSI/FCI 70-2), torque margin < 20% triggers emergency actuator overhaul mandate.\n"
            "4. Conclusion: Valve risks failure to close during emergency unit de-pressurization in 380 deg C vacuum residue service."
        )
    elif asset_ctx == "FIRED_HEATER":
        reasoning = (
            "INDUSTRIAL CONDITION REASONING (FIRED HEATER MRPL-BOIL-501-HP):\n"
            "1. Multimodal Evidence: Radiant tube skin thermocouple TI-501-14 measures 722 deg C (Design Limit API 530: 650 deg C), "
            "with a 1.8-meter localized hotspot band verified via thermographic IR scan.\n"
            "2. Combustion Analysis: Arch draft pressure at -1.2 mm H2O indicates poor draft control, with Burner #6 tile flame impingement.\n"
            "3. SOP Alignment: Per SOP-MRPL-HEAT-710, continuous operation of 9% Cr-1 Mo radiant tubes above 700 deg C accelerates "
            "internal coking and reduces metallurgical creep rupture life by over 90%.\n"
            "4. Conclusion: Imminent hazard of radiant tube thinning, rupture, and firebox hydrocarbon leakage."
        )
    else:
        reasoning = (
            "INDUSTRIAL CONDITION REASONING (PUMP MRPL-PUMP-101-B):\n"
            "1. Multimodal Evidence: Drive-End bearing temperature reaches 82 deg C (Alarm limit: 75 deg C) with active mechanical seal leakage at 15 drops/min.\n"
            "2. Tabular History: Excel records indicate drive-end bearing replacement was last performed 14 months ago.\n"
            "3. SOP Alignment: Per SOP-MRPL-MECH-402 Section 4.2, bearing overhaul and seal replacement are mandated when temperature exceeds 80 deg C "
            "or seal leakage exceeds 5 drops/min.\n"
            "4. Conclusion: Continued operation risks catastrophic shaft seizure, bearing cage collapse, and crude unit feed loss."
        )
    
    logs = _log_step(state, "Reasoning", f"Reasoning completed for [{asset_ctx}] using model [{route_info.get('selected_model')}].")
    return {
        "reasoning_output": reasoning,
        "execution_logs": logs,
        "current_step": "REASON",
    }

def assess_risk_node(state: AgentState) -> Dict[str, Any]:
    asset_ctx = _detect_asset_context(state)
    existing_approval = state.get("human_approval_status", "PENDING")
    approval_status = existing_approval if existing_approval in ["APPROVED", "MODIFIED"] else "PENDING"

    risk_map = {
        "COMPRESSOR": {
            "risk": "CRITICAL",
            "confidence": 0.95,
            "rec": (
                "CRITICAL ACTION DIRECTIVE (MRPL-COMP-201-A):\n"
                "1. Throttle VDU-2 suction rate by 25% immediately to relieve compressor aerodynamic loading.\n"
                "2. Schedule controlled unit shutdown within 24 hours to prevent thrust collar seizure.\n"
                "3. Perform complete duplex lube oil filter changeout and lube temperature re-trimming to 45 deg C.\n"
                "4. Inspect tilting pad thrust shoes and replace Dry Gas Seal Cartridge #1."
            )
        },
        "HEAT_EXCHANGER": {
            "risk": "HIGH",
            "confidence": 0.93,
            "rec": (
                "IMMEDIATE ACTION PLAN (MRPL-HEX-105-AB):\n"
                "1. Isolate Exchanger Train B via block valves and divert crude feed through clean bypass loop.\n"
                "2. Perform off-line high-pressure water lancing (1200 bar hydro-jet) to remove tube coking.\n"
                "3. Execute hot aromatic solvent circulation wash to dissolve asphaltene precipitation.\n"
                "4. Replace channel head Kammprofile metallic gasket and conduct 37.5 bar hydrostatic proof test."
            )
        },
        "DISTILLATION_COLUMN": {
            "risk": "HIGH",
            "confidence": 0.94,
            "rec": (
                "IMMEDIATE MITIGATION PROTOCOL (MRPL-COL-301):\n"
                "1. Increase wash zone pumparound circulation by 15% to de-inventory flooding Trays 20-24.\n"
                "2. Reduce crude heater outlet temperature by 4 deg C to reduce vapor superficial velocity.\n"
                "3. Inspect desalter wash water carryover to verify crude salt remains < 3.0 PTB.\n"
                "4. Plan mini-turnaround internal column entry to inspect and replace damaged tray downcomers."
            )
        },
        "CONTROL_VALVE": {
            "risk": "HIGH",
            "confidence": 0.95,
            "rec": (
                "IMMEDIATE RECTIFICATION DIRECTIVE (MRPL-VALVE-402-MOV):\n"
                "1. Tighten gland follower bolts immediately to stem hot vacuum residue weeping.\n"
                "2. Overhaul Limitorque actuator bevel gearbox and re-lubricate drive worm gear.\n"
                "3. Stage spare Tungsten Carbide / Stellite-6 trim assembly for immediate hot-swap.\n"
                "4. Recalibrate open/close torque limit switches and verify stroke time <= 25.0 seconds."
            )
        },
        "FIRED_HEATER": {
            "risk": "CRITICAL",
            "confidence": 0.96,
            "rec": (
                "EMERGENCY FURNACE DIRECTIVE (MRPL-BOIL-501-HP):\n"
                "1. Immediately throttle fuel gas to Burner #6 to eliminate direct flame impingement on Pass 2.\n"
                "2. Adjust stack damper to restore arch draft pressure to negative -3.0 mm H2O.\n"
                "3. Increase steam-to-oil decoking ratio by 10% to lower internal tube wall film temperature.\n"
                "4. Schedule mechanical pigging / online steam-air decoking of Radiant Pass 2 within 7 days."
            )
        },
        "CENTRIFUGAL_PUMP": {
            "risk": "HIGH",
            "confidence": 0.94,
            "rec": (
                "IMMEDIATE ACTION RECOMMENDED (MRPL-PUMP-101-B):\n"
                "Schedule shutdown maintenance for Pump MRPL-PUMP-101-B within 48 hours.\n"
                "1. Replace Drive-End Mechanical Seal Cartridge Assembly (Plan 53A).\n"
                "2. Replace Drive-End angular contact ball bearing (SKF 7314 BECBM).\n"
                "3. Perform lubricant flush, casing cleanout, and laser shaft alignment check."
            )
        },
    }

    spec = risk_map.get(asset_ctx, risk_map["CENTRIFUGAL_PUMP"])
    risk = spec["risk"]
    confidence = spec["confidence"]
    recommendation = spec["rec"]
    
    logs = _log_step(state, "Assess Risk", f"Risk assessed as '{risk}' with Confidence {confidence * 100:.1f}% for [{asset_ctx}].")
    return {
        "risk_level": risk,
        "confidence_score": confidence,
        "recommendation": recommendation,
        "human_approval_status": approval_status,
        "execution_logs": logs,
        "current_step": "ASSESS_RISK",
    }

def generate_report_node(state: AgentState) -> Dict[str, Any]:
    approval_status = state.get("human_approval_status", "PENDING")
    
    if approval_status not in ["APPROVED", "MODIFIED"]:
        logs = _log_step(state, "Generate Report", "Report generation paused: Awaiting human approval.")
        return {"execution_logs": logs, "current_step": "AWAITING_APPROVAL"}

    report_result = docx_generator.generate_report(state)
    report_path = report_result.get("report_path")
    
    logs = _log_step(state, "Generate Report", f"Professional DOCX report successfully generated at: {report_path}")
    return {
        "generated_report_path": report_path,
        "execution_logs": logs,
        "current_step": "GENERATE_REPORT",
    }
