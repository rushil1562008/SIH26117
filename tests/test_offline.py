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
from rag.retriever import retriever

class TestSovereignAirGapOffline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_synthetic_demo_files()
        retriever.reindex()

    def test_air_gap_policy(self):
        self.assertTrue(config.air_gapped_mode)
        self.assertFalse(config.external_api_allowed)
        print("[PASS] Air-Gap Configuration Policy Verified")

    def test_zero_external_network_calls(self):
        summary = network_monitor.get_security_summary()
        self.assertEqual(summary["external_api_calls"], 0)
        self.assertEqual(summary["air_gapped_status"], "AIR_GAPPED_SECURE")
        print("[PASS] Security Network Log Verified: External API Calls = 0")

    def test_19_refinery_files_integrity(self):
        """Verifies all 19 new files (and 4 baseline files) are correctly generated and well-formed."""
        # 1. Documents: 5 new + 1 baseline = 6
        expected_docs = [
            "sample_pump_inspection.pdf",
            "pump_inspection_02.pdf",
            "pump_inspection_03.pdf",
            "pump_inspection_04.pdf",
            "pump_inspection_05.pdf",
            "pump_inspection_06.pdf",
        ]
        for fname in expected_docs:
            p = config.documents_dir / fname
            self.assertTrue(p.exists(), f"Missing document: {fname}")
            self.assertGreater(p.stat().st_size, 500, f"Document {fname} is empty or corrupted")

        # 2. Images: 5 new + 1 baseline = 6
        from PIL import Image
        expected_imgs = [
            "sample_pump_image.jpg",
            "pump_image_02.jpg",
            "pump_image_03.jpg",
            "pump_image_04.jpg",
            "pump_image_05.jpg",
            "pump_image_06.jpg",
        ]
        for fname in expected_imgs:
            p = config.images_dir / fname
            self.assertTrue(p.exists(), f"Missing image: {fname}")
            with Image.open(p) as img:
                self.assertGreaterEqual(img.size[0], 600)
                self.assertGreaterEqual(img.size[1], 400)

        # 3. Knowledge Base: 5 new + 1 baseline = 6
        expected_kbs = [
            "sample_maintenance_sop.pdf",
            "maintenance_sop_02.pdf",
            "maintenance_sop_03.pdf",
            "maintenance_sop_04.pdf",
            "maintenance_sop_05.pdf",
            "maintenance_sop_06.pdf",
        ]
        for fname in expected_kbs:
            p = config.knowledge_base_dir / fname
            self.assertTrue(p.exists(), f"Missing knowledge base file: {fname}")
            self.assertGreater(p.stat().st_size, 500)

        # 4. Tables: 4 new + 1 baseline = 5
        import pandas as pd
        expected_tables = [
            "sample_maintenance_history.xlsx",
            "maintenance_history_02.xlsx",
            "maintenance_history_03.xlsx",
            "maintenance_history_04.xlsx",
            "maintenance_history_05.xlsx",
        ]
        for fname in expected_tables:
            p = config.tables_dir / fname
            self.assertTrue(p.exists(), f"Missing table file: {fname}")
            xl = pd.ExcelFile(p)
            self.assertGreaterEqual(len(xl.sheet_names), 1)
            df = pd.read_excel(p)
            self.assertGreater(len(df), 2, f"Table {fname} has insufficient rows")

        print("[PASS] All 19 new refinery asset files + 4 baseline files verified successfully!")

    def test_local_rag_indexing_and_citation_retrieval(self):
        """Verifies that all 6 knowledge base SOPs are indexed and accurately retrieved."""
        indexed_count = retriever.reindex()
        self.assertGreaterEqual(indexed_count, 6, "Knowledge base did not index all 6 SOPs")

        # Query Compressor SOP
        comp_cit = retriever.retrieve("centrifugal compressor vibration trip limits API 617", top_k=2)
        self.assertGreater(len(comp_cit), 0)
        self.assertTrue(any("maintenance_sop_02" in c["filename"] for c in comp_cit), "Compressor SOP was not prioritized")

        # Query Heat Exchanger SOP
        hex_cit = retriever.retrieve("heat exchanger fouling delta P TEMA Class R cleaning", top_k=2)
        self.assertGreater(len(hex_cit), 0)
        self.assertTrue(any("maintenance_sop_03" in c["filename"] for c in hex_cit), "Heat Exchanger SOP was not prioritized")

        print("[PASS] Local RAG indexing and multi-SOP citation retrieval verified")

    def test_end_to_end_agent_workflow(self):
        """Verifies end-to-end execution for baseline Centrifugal Pump."""
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
        print("[PASS] End-to-End Agent Workflow (Pump): Report at", final_state["generated_report_path"])

    def test_multi_asset_compressor_workflow(self):
        """Verifies end-to-end execution for Asset 02: VDU Wet Gas Centrifugal Compressor."""
        initial_state: AgentState = {
            "task_description": "Analyze wet gas compressor stage-1 high radial vibration, thrust bearing temperature, and lube oil anomalies.",
            "task_type": "MULTIMODAL_AGENT",
            "pdf_path": str(config.documents_dir / "pump_inspection_02.pdf"),
            "image_path": str(config.images_dir / "pump_image_02.jpg"),
            "excel_path": str(config.tables_dir / "maintenance_history_02.xlsx"),
            "plan": [],
            "raw_evidence": {},
            "rag_citations": [],
            "fused_evidence": "",
            "reasoning_output": "",
            "risk_level": "PENDING",
            "confidence_score": 0.0,
            "recommendation": "",
            "human_approval_status": "APPROVED",
            "approver_notes": "Operations Manager Sign-off",
            "generated_report_path": None,
            "execution_logs": [],
            "current_step": "START",
            "model_routing_info": {},
        }

        final_state = agent_graph.run(initial_state)

        self.assertEqual(final_state["current_step"], "GENERATE_REPORT")
        self.assertIn(final_state["risk_level"], ["CRITICAL", "HIGH"])
        self.assertIn("COMP-201", final_state["reasoning_output"])
        self.assertTrue(Path(final_state["generated_report_path"]).exists())
        print("[PASS] End-to-End Multi-Asset Workflow (Compressor): Report at", final_state["generated_report_path"])

if __name__ == "__main__":
    unittest.main()
