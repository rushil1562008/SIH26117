import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import config
from security.policy import security_policy
from security.network_monitor import network_monitor
from models.hardware import detector
from models.router import router
from agents.graph import agent_graph
from agents.state import AgentState
from generate_demo_data import create_synthetic_demo_files
from reports.docx_generator import docx_generator

class TestSovereignAirGapOffline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_synthetic_demo_files()

    def test_air_gap_policy(self):
        self.assertTrue(config.air_gapped_mode)
        self.assertFalse(config.external_api_allowed)
        print("✓ Air-Gap Configuration Policy Verified")

    def test_zero_external_network_calls(self):
        summary = network_monitor.get_security_summary()
        self.assertEqual(summary["external_api_calls"], 0)
        self.assertEqual(summary["air_gapped_status"], "AIR_GAPPED_SECURE")
        print("✓ Security Network Log Verified: External API Calls = 0")

    def test_end_to_end_agent_workflow(self):
        pdf_path = str(config.documents_dir / "sample_pump_inspection.pdf")
        if not Path(pdf_path).exists():
            pdf_path = str(config.documents_dir / "sample_pump_inspection.txt")

        initial_state: AgentState = {
            "task_description": "Analyze pump inspection and determine whether maintenance is required.",
            "task_type": "MULTIMODAL_AGENT",
            "pdf_path": pdf_path,
            "image_path": str(config.images_dir / "sample_pump_image.jpg"),
            "excel_path": str(config.tables_dir / "sample_maintenance_history.xlsx"),
            "plan": [],
            "raw_evidence": {},
            "rag_citations": [],
            "fused_evidence": "",
            "reasoning_output": "",
            "risk_level": "PENDING",
            "confidence_score": 0.0,
            "recommendation": "",
            "human_approval_status": "APPROVED",
            "approver_notes": "Automated Offline Test Approval",
            "generated_report_path": None,
            "execution_logs": [],
            "current_step": "START",
            "model_routing_info": {},
        }

        final_state = agent_graph.run(initial_state)

        self.assertEqual(final_state["current_step"], "GENERATE_REPORT")
        self.assertEqual(final_state["risk_level"], "HIGH")
        self.assertGreater(final_state["confidence_score"], 0.8)
        self.assertTrue(Path(final_state["generated_report_path"]).exists())
        
        # Verify network calls remained 0 throughout workflow
        self.assertEqual(network_monitor.external_calls_count, 0)
        print("✓ End-to-End Agent Workflow Passed: Report generated at", final_state["generated_report_path"])

if __name__ == "__main__":
    unittest.main()
