import os
from pathlib import Path
from typing import Tuple, Dict, Any, List
import gradio as gr

from app.config import config
from models.hardware import detector
from models.router import router
from agents.graph import agent_graph
from agents.state import AgentState
from security.network_monitor import network_monitor
from tools.code_executor import code_executor
from tools.calculator import calculator
from reports.docx_generator import docx_generator
from reports.pdf_generator import pdf_generator
from reports.xlsx_generator import xlsx_generator
from reports.pptx_generator import pptx_generator

# Global active state store for approval workflow
CURRENT_AGENT_STATE: Dict[str, Any] = {}

ASSET_PRESETS = {
    "MRPL-PUMP-101-B: CDU Crude Feed Centrifugal Pump (Sample 01)": {
        "task": "Analyze crude feed pump inspection and determine required maintenance actions.",
        "pdf": "sample_pump_inspection.pdf",
        "img": "sample_pump_image.jpg",
        "xls": "sample_maintenance_history.xlsx",
    },
    "MRPL-COMP-201-A: VDU Wet Gas Centrifugal Compressor (Asset 02)": {
        "task": "Analyze wet gas compressor stage-1 high radial vibration, thrust bearing temperature, and lube oil anomalies.",
        "pdf": "pump_inspection_02.pdf",
        "img": "pump_image_02.jpg",
        "xls": "maintenance_history_02.xlsx",
    },
    "MRPL-HEX-105-AB: CDU Shell & Tube Heat Exchanger (Asset 03)": {
        "task": "Evaluate crude pre-heat exchanger fouling, severe shell-side delta-P excursion, and U-value degradation.",
        "pdf": "pump_inspection_03.pdf",
        "img": "pump_image_03.jpg",
        "xls": "maintenance_history_03.xlsx",
    },
    "MRPL-COL-301: CDU Atmospheric Distillation Column (Asset 04)": {
        "task": "Assess distillation column flooding, high differential pressure across trays 20-24, and top temperature rise.",
        "pdf": "pump_inspection_04.pdf",
        "img": "pump_image_04.jpg",
        "xls": "maintenance_history_04.xlsx",
    },
    "MRPL-VALVE-402-MOV: VDU Severe Service Letdown Valve (Asset 05)": {
        "task": "Diagnose vacuum bottoms letdown MOV actuator torque deficit, acoustic cavitation, and seat passing.",
        "pdf": "pump_inspection_05.pdf",
        "img": "pump_image_05.jpg",
        "xls": "maintenance_history_05.xlsx",
    },
    "MRPL-BOIL-501-HP: CDU Fired Heater Radiant Superheater (Asset 06)": {
        "task": "Evaluate radiant tube skin thermocouple hot spot (722 deg C), flame impingement, and API 530 creep rupture risks.",
        "pdf": "pump_inspection_06.pdf",
        "img": "pump_image_06.jpg",
        "xls": "sample_maintenance_history.xlsx",
    },
    "Custom Upload: Use custom uploaded files below": {
        "task": "Analyze uploaded industrial equipment files.",
        "pdf": None,
        "img": None,
        "xls": None,
    }
}

def refresh_hardware_display() -> str:
    return detector.get_formatted_table()

def refresh_security_display() -> str:
    return network_monitor.get_formatted_log()

def run_agent_workflow(
    task_desc: str,
    pdf_file,
    img_file,
    xls_file,
    preset_name: str = "MRPL-PUMP-101-B: CDU Crude Feed Centrifugal Pump (Sample 01)",
) -> Tuple[str, str, str, str, str, str, str, str, str]:
    """Runs the evidence-to-action industrial agent workflow with multi-asset preset support."""
    global CURRENT_AGENT_STATE

    preset_cfg = ASSET_PRESETS.get(preset_name, ASSET_PRESETS["MRPL-PUMP-101-B: CDU Crude Feed Centrifugal Pump (Sample 01)"])
    default_pdf = preset_cfg.get("pdf") or "sample_pump_inspection.pdf"
    default_img = preset_cfg.get("img") or "sample_pump_image.jpg"
    default_xls = preset_cfg.get("xls") or "sample_maintenance_history.xlsx"

    pdf_path = pdf_file.name if pdf_file else str(config.documents_dir / default_pdf)
    img_path = img_file.name if img_file else str(config.images_dir / default_img)
    xls_path = xls_file.name if xls_file else str(config.tables_dir / default_xls)

    # Fallback to TXT if PDF not found
    if not Path(pdf_path).exists() and Path(pdf_path).with_suffix(".txt").exists():
        pdf_path = str(Path(pdf_path).with_suffix(".txt"))

    initial_state: AgentState = {
        "task_description": task_desc or preset_cfg.get("task", "Analyze industrial inspection"),
        "task_type": "MULTIMODAL_AGENT",
        "pdf_path": pdf_path if Path(pdf_path).exists() else None,
        "image_path": img_path if Path(img_path).exists() else None,
        "excel_path": xls_path if Path(xls_path).exists() else None,
        "plan": [],
        "raw_evidence": {},
        "rag_citations": [],
        "fused_evidence": "",
        "reasoning_output": "",
        "risk_level": "PENDING",
        "confidence_score": 0.0,
        "recommendation": "",
        "human_approval_status": "PENDING",
        "approver_notes": "",
        "generated_report_path": None,
        "execution_logs": [],
        "current_step": "START",
        "model_routing_info": {},
    }

    final_state = agent_graph.run(initial_state)
    CURRENT_AGENT_STATE = dict(final_state)

    # Format outputs
    route_info = final_state.get("model_routing_info", {})
    router_summary = (
        f"=== MODEL ROUTER DECISION ===\n"
        f"Task Type        : {route_info.get('task_type')}\n"
        f"Selected Model   : {route_info.get('selected_model')}\n"
        f"Provider         : {route_info.get('provider_type')}\n"
        f"Quantization     : {route_info.get('quantization')}\n"
        f"Hardware Profile : {route_info.get('detected_profile')}\n"
        f"Available VRAM   : {route_info.get('available_vram_mb')} MB\n"
        f"Fallback Active  : {route_info.get('fallback_mode_active')}\n"
        f"Routing Rationale: {route_info.get('fallback_reason')}\n"
        f"=============================="
    )

    logs_text = "\n".join(final_state.get("execution_logs", []))
    evidence_text = final_state.get("fused_evidence", "No evidence extracted.")
    reasoning_text = final_state.get("reasoning_output", "")
    risk_text = f"RISK LEVEL: {final_state.get('risk_level')}\nCONFIDENCE SCORE: {final_state.get('confidence_score', 0.0) * 100:.1f}%"
    recommendation_text = final_state.get("recommendation", "")
    approval_status_text = f"STATUS: {final_state.get('human_approval_status')}\n(Awaiting Human Approval to seal executive report deliverable)"
    security_text = network_monitor.get_formatted_log()
    hw_text = detector.get_formatted_table()

    return (
        router_summary,
        logs_text,
        evidence_text,
        reasoning_text,
        risk_text,
        recommendation_text,
        approval_status_text,
        security_text,
        hw_text,
    )

def handle_human_approval(approver_notes: str, action: str) -> Tuple[str, str, str, str]:
    """Processes human approval gate action (APPROVE, MODIFY, REJECT) and generates reports."""
    global CURRENT_AGENT_STATE

    if not CURRENT_AGENT_STATE:
        return "No active agent run found. Please run the task analysis first.", None, None, None

    status_map = {
        "APPROVE RECOMMENDATION": "APPROVED",
        "MODIFY RECOMMENDATION": "MODIFIED",
        "REJECT RECOMMENDATION": "REJECTED",
    }
    status = status_map.get(action, "APPROVED")
    CURRENT_AGENT_STATE["human_approval_status"] = status
    CURRENT_AGENT_STATE["approver_notes"] = approver_notes or "Verified by Plant Engineer."

    if status in ["APPROVED", "MODIFIED"]:
        docx_res = docx_generator.generate_report(CURRENT_AGENT_STATE)
        pdf_res = pdf_generator.generate_report(CURRENT_AGENT_STATE)
        xlsx_res = xlsx_generator.generate_report(CURRENT_AGENT_STATE)
        pptx_res = pptx_generator.generate_report(CURRENT_AGENT_STATE)

        docx_file = docx_res.get("report_path")
        pdf_file = pdf_res.get("report_path")
        xlsx_file = xlsx_res.get("report_path")
        pptx_file = pptx_res.get("report_path")

        msg = (
            f"✅ HUMAN APPROVAL STAMPED ({status})!\n"
            f"Executive deliverables generated in local outputs/ folder:\n"
            f"1. Word Document: {docx_res['filename']}\n"
            f"2. PDF Document : {pdf_res['filename']}\n"
            f"3. Excel Summary : {xlsx_res['filename']}\n"
            f"4. PowerPoint    : {pptx_res['filename']}"
        )
        return msg, docx_file, pdf_file, xlsx_file
    else:
        return f"❌ Recommendation REJECTED by human operator. No final report generated.", None, None, None

def run_coding_demo(
    flow_rate: float,
    head: float,
    power: float,
) -> Tuple[str, str, str]:
    """Runs the sandboxed coding and calculation demonstration."""
    calc_res = calculator.calculate_pump_efficiency(flow_rate, head, power)
    
    python_code = (
        f"# Generated Python script for pump efficiency calculation\n"
        f"def calculate_pump_efficiency(flow_m3h, head_m, power_kw):\n"
        f"    density = 1000.0\n"
        f"    g = 9.81\n"
        f"    flow_m3s = flow_m3h / 3600.0\n"
        f"    hydraulic_power = (density * g * flow_m3s * head_m) / 1000.0\n"
        f"    efficiency = (hydraulic_power / power_kw) * 100.0\n"
        f"    return round(efficiency, 2), round(hydraulic_power, 2)\n\n"
        f"eff, hyd_pwr = calculate_pump_efficiency({flow_rate}, {head}, {power})\n"
        f"print(f'Hydraulic Power: {{hyd_pwr}} kW')\n"
        f"print(f'Pump Efficiency: {{eff}}%')\n"
    )

    exec_res = code_executor.execute_python(python_code)
    
    code_display = python_code
    sandbox_output = (
        f"Execution Status: {exec_res['status']}\n"
        f"Exit Code       : {exec_res['exit_code']}\n"
        f"Standard Output :\n{exec_res['stdout']}\n"
        f"Standard Error  :\n{exec_res['stderr']}"
    )
    calc_steps = calc_res["calculation_steps"]

    return code_display, sandbox_output, calc_steps

def create_ui() -> gr.Blocks:
    """Constructs the Gradio Industrial Workbench interface."""

    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="gray",
    )

    with gr.Blocks(theme=theme, title="MRPL Sovereign AI Workbench") as demo:
        gr.Markdown(
            """
            # 🏭 MRPL Sovereign On-Premise Agentic AI Workbench
            ### Problem Statement SIH26117 | Smart Automation Theme | Air-Gapped Confidential Industrial Processing
            ---
            """
        )

        with gr.Tab("Golden Demo: Evidence-to-Action Agent"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 1. Asset Preset & Input Files")
                    preset_selector = gr.Dropdown(
                        label="Select Refinery Asset Preset",
                        choices=list(ASSET_PRESETS.keys()),
                        value="MRPL-PUMP-101-B: CDU Crude Feed Centrifugal Pump (Sample 01)",
                    )
                    task_input = gr.Textbox(
                        label="Task Description",
                        value=ASSET_PRESETS["MRPL-PUMP-101-B: CDU Crude Feed Centrifugal Pump (Sample 01)"]["task"],
                        lines=2,
                    )
                    pdf_input = gr.File(label="Upload Inspection PDF (Optional if preset chosen)", file_types=[".pdf", ".txt"])
                    img_input = gr.File(label="Upload Equipment Photo/Scan (Optional if preset chosen)", file_types=[".jpg", ".png"])
                    xls_input = gr.File(label="Upload Maintenance History (Optional if preset chosen)", file_types=[".xlsx", ".csv"])

                    run_btn = gr.Button("🚀 Execute Industrial Agent Workflow", variant="primary")

                    gr.Markdown("---")
                    gr.Markdown("### 2. Hardware Status & Router")
                    hw_box = gr.Textbox(label="Runtime Hardware Specs", value=refresh_hardware_display, lines=8)
                    router_box = gr.Textbox(label="Task & Hardware Router Decision", lines=8)

                with gr.Column(scale=2):
                    gr.Markdown("### 3. Agent Execution Timeline & Logs")
                    logs_box = gr.Textbox(label="Agent Workflow Log", lines=6)

                    with gr.Accordion("4. Unified Evidence Context (Multimodal + Local RAG)", open=True):
                        evidence_box = gr.Textbox(label="Fused Source Evidence", lines=8)

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 5. Condition Reasoning")
                            reasoning_box = gr.Textbox(label="AI Assessment & RAG Cross-Reference", lines=6)
                        with gr.Column():
                            gr.Markdown("### 6. Risk & Recommendation")
                            risk_box = gr.Textbox(label="Risk & Confidence Level", lines=2)
                            recommendation_box = gr.Textbox(label="Maintenance Recommendation", lines=4)

                    gr.Markdown("---")
                    gr.Markdown("### 7. Human Approval Gate & Deliverables")
                    approval_status_box = gr.Textbox(label="Approval Gate Status", value="STATUS: PENDING", lines=2)
                    approver_notes = gr.Textbox(label="Approver Engineering Notes", value="Verified by MRPL Operations Manager.")

                    with gr.Row():
                        approve_btn = gr.Button("✅ APPROVE RECOMMENDATION", variant="primary")
                        modify_btn = gr.Button("✏️ MODIFY RECOMMENDATION", variant="secondary")
                        reject_btn = gr.Button("❌ REJECT RECOMMENDATION", variant="stop")

                    approval_result_box = gr.Textbox(label="Deliverable Generation Status", lines=3)
                    
                    with gr.Row():
                        out_docx = gr.File(label="Download DOCX Report")
                        out_pdf = gr.File(label="Download PDF Report")
                        out_xlsx = gr.File(label="Download XLSX Summary")

        with gr.Tab("Sandboxed Coding & Calculation Demo"):
            gr.Markdown("### Verified Engineering Calculation & Code Execution Sandbox")
            with gr.Row():
                with gr.Column():
                    flow_in = gr.Number(label="Flow Rate (m³/h)", value=150.0)
                    head_in = gr.Number(label="Differential Head (m)", value=45.0)
                    power_in = gr.Number(label="Shaft Power (kW)", value=25.0)
                    calc_btn = gr.Button("⚡ Generate Code & Execute Sandbox", variant="primary")

                with gr.Column():
                    code_box = gr.Textbox(label="Generated Python Code", lines=10)
                    sandbox_box = gr.Textbox(label="Sandboxed Execution Output", lines=8)
                    steps_box = gr.Textbox(label="Step-by-Step Calculation Formula", lines=12)

        with gr.Tab("Security & Air-Gap Audit"):
            gr.Markdown("### Sovereign Sovereignty & Air-Gap Verification Monitor")
            sec_box = gr.Textbox(label="Security Network Log", value=refresh_security_display, lines=8)
            refresh_sec_btn = gr.Button("🔄 Refresh Security Audit")

        # Preset change event
        def on_preset_selected(choice):
            cfg = ASSET_PRESETS.get(choice, {})
            return cfg.get("task", "")

        preset_selector.change(
            fn=on_preset_selected,
            inputs=[preset_selector],
            outputs=[task_input],
        )

        # Event Handlers
        run_btn.click(
            fn=run_agent_workflow,
            inputs=[task_input, pdf_input, img_input, xls_input, preset_selector],
            outputs=[
                router_box,
                logs_box,
                evidence_box,
                reasoning_box,
                risk_box,
                recommendation_box,
                approval_status_box,
                sec_box,
                hw_box,
            ],
        )

        approve_btn.click(
            fn=lambda notes: handle_human_approval(notes, "APPROVE RECOMMENDATION"),
            inputs=[approver_notes],
            outputs=[approval_result_box, out_docx, out_pdf, out_xlsx],
        )

        modify_btn.click(
            fn=lambda notes: handle_human_approval(notes, "MODIFY RECOMMENDATION"),
            inputs=[approver_notes],
            outputs=[approval_result_box, out_docx, out_pdf, out_xlsx],
        )

        reject_btn.click(
            fn=lambda notes: handle_human_approval(notes, "REJECT RECOMMENDATION"),
            inputs=[approver_notes],
            outputs=[approval_result_box, out_docx, out_pdf, out_xlsx],
        )

        calc_btn.click(
            fn=run_coding_demo,
            inputs=[flow_in, head_in, power_in],
            outputs=[code_box, sandbox_box, steps_box],
        )

        refresh_sec_btn.click(
            fn=refresh_security_display,
            inputs=[],
            outputs=[sec_box],
        )

    return demo
