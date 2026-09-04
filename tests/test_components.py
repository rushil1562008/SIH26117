import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.hardware import detector
from models.router import router
from rag.embeddings import embedding_engine
from rag.vector_store import LocalVectorStore
from tools.calculator import calculator
from tools.code_executor import code_executor
from tools.excel_tool import excel_tool
from reports.docx_generator import docx_generator
from app.config import config

class TestWorkbenchComponents(unittest.TestCase):

    def test_hardware_detector(self):
        summary = detector.get_summary()
        self.assertIn("cpu", summary)
        self.assertIn("ram_gb", summary)
        self.assertIn("detected_profile", summary)
        print("✓ Hardware Detector Test Passed:", summary["detected_profile"])

    def test_model_router(self):
        provider, meta = router.route("TEXT_REASONING")
        self.assertIn("selected_model", meta)
        self.assertIn("provider_type", meta)
        print("✓ Model Router Test Passed:", meta["selected_model"])

    def test_local_vector_store(self):
        store = LocalVectorStore(embedder=embedding_engine)
        store.add_chunks([
            {"chunk_id": "c1", "text": "Pump bearing temperature limit is 75 C", "filename": "sop.pdf", "page": 12},
            {"chunk_id": "c2", "text": "Electrical transformer oil test procedure", "filename": "elec.pdf", "page": 3},
        ])
        results = store.search("bearing temperature limit", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0]["chunk_id"], "c1")
        print("✓ Local Vector Store Test Passed")

    def test_calculator(self):
        res = calculator.calculate_pump_efficiency(150.0, 45.0, 25.0)
        self.assertGreater(res["efficiency_pct"], 0)
        self.assertIn("P_hyd", res["calculation_steps"])
        print("✓ Engineering Calculator Test Passed:", res["efficiency_pct"], "%")

    def test_sandbox_executor(self):
        code = "print(10 + 20)"
        res = code_executor.execute_python(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["stdout"], "30")
        print("✓ Sandbox Executor Test Passed")

    def test_report_generator(self):
        mock_state = {
            "model_routing_info": {"selected_model": "test_model", "provider_type": "local", "detected_profile": "RTX_3050", "available_vram_mb": 4096},
            "risk_level": "HIGH",
            "confidence_score": 0.94,
            "fused_evidence": "Mock fused evidence",
            "rag_citations": [{"source_citation": "sop.pdf — Page 12", "text": "Limit 75 C"}],
            "reasoning_output": "Mock reasoning",
            "recommendation": "Mock recommendation",
            "human_approval_status": "APPROVED",
            "approver_notes": "Tested by unit test",
        }
        res = docx_generator.generate_report(mock_state)
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["report_path"]).exists())
        print("✓ DOCX Report Generator Test Passed:", res["filename"])

if __name__ == "__main__":
    unittest.main()
