# Sovereign On-Premise Agentic AI Workbench for Confidential Industrial Work

**Problem Statement ID**: SIH26117 / S.No. 117  
**Organization**: Mangalore Refinery and Petrochemicals Limited (MRPL)  
**Theme**: Smart Automation | **Category**: Software  
**Target Hackathon Round**: Internal Selection (10 September 2026)

---

## 🌟 Key Features

1. **Air-Gapped Sovereign Security**: Operates with **0 external API calls** during confidential processing. Enforces `AIR_GAPPED_MODE=true` and active network socket auditing.
2. **Task & Hardware-Aware Model Router**:
   - Dynamic runtime detection of CPU, RAM, GPU, VRAM, and CUDA capabilities.
   - Presets and fallback models for NVIDIA Tesla T4 (~16GB), RTX 3050 (~4GB), Quadro P2000 (5GB), and CPU fallback.
3. **Multi-Tier Model Provider Architecture**:
   - **Ollama Provider**: Connects locally to Ollama (`http://127.0.0.1:11434`).
   - **Transformers Provider**: Direct PyTorch/HuggingFace offline execution.
   - **Sovereign Local Fallback Engine**: Rule-based local reasoning engine ensuring **0 application crashes** under any hardware environment.
4. **Evidence-to-Action Industrial Agent (LangGraph)**:
   - Explicit state transitions: `START -> UNDERSTAND_TASK -> PLAN -> COLLECT_INPUTS -> SEARCH_KNOWLEDGE (RAG) -> ANALYZE_DOCUMENTS -> ANALYZE_IMAGE -> ANALYZE_TABLE -> FUSE_EVIDENCE -> REASON -> ASSESS_RISK -> GENERATE_RECOMMENDATION -> HUMAN_APPROVAL -> GENERATE_REPORT -> END`.
5. **Multimodal Evidence Fusion & Local RAG**:
   - Combines PDF inspection reports, pump photos (with OCR and visual analysis), Excel maintenance history spreadsheets, and local SOP manuals with page-level citations.
6. **Sandboxed Code Execution & Deterministic Calculator**:
   - Runs generated Python code in an isolated temporary directory with execution timeouts, stdout/stderr capture, and AST safety verification.
   - Deterministic engineering calculator for flow rate, differential head, hydraulic power, and pump efficiency.
7. **Human Approval Gate & Report Generator**:
   - AI recommendations must be approved/modified by a human operator before executive DOCX, PDF, XLSX, and PPTX reports are produced.

---

## 📁 Project Structure

```
sih26117/
├── app/
│   ├── main.py             # Application entrypoint
│   ├── ui.py               # Gradio Industrial Dashboard (11 sections)
│   └── config.py           # Sovereign configuration & path management
├── models/
│   ├── hardware.py         # Runtime hardware detector (GPU, VRAM, CUDA, RAM)
│   ├── base_model.py       # Model providers (Ollama, Transformers, Fallback)
│   ├── registry.py         # Model specifications & hardware profiles
│   └── router.py           # Task & Hardware-aware router
├── rag/
│   ├── ingest.py           # PDF/TXT document chunking & metadata extractor
│   ├── embeddings.py       # Local offline embedding engine
│   ├── vector_store.py     # Local cosine similarity vector store
│   └── retriever.py        # Semantic retriever with source citations
├── multimodal/
│   └── pipeline.py         # Multimodal evidence fusion (Text + PDF + OCR + Excel)
├── tools/
│   ├── pdf_tool.py         # PDF text reader
│   ├── ocr_tool.py         # Offline OCR extractor
│   ├── excel_tool.py       # Spreadsheet analyzer
│   ├── image_tool.py       # Industrial photograph visual analyzer
│   ├── calculator.py       # Deterministic engineering calculator
│   ├── code_executor.py    # Sandboxed Python code executor
│   └── file_tools.py       # Safe local file reader/writer
├── agents/
│   ├── state.py            # LangGraph agent state schema
│   ├── nodes.py            # Execution nodes for each state
│   └── graph.py            # LangGraph state machine builder
├── reports/
│   ├── docx_generator.py   # Executive Word report generator
│   ├── pdf_generator.py    # PDF deliverable generator
│   ├── xlsx_generator.py   # Excel summary deliverable generator
│   └── pptx_generator.py   # PowerPoint summary deliverable generator
├── security/
│   ├── network_monitor.py  # Socket monitor verifying External API Calls = 0
│   ├── policy.py           # Air-gap policy enforcement
│   └── audit_logger.py     # Structured file logging
├── config/
│   ├── models.yaml         # Model specifications & VRAM requirements
│   └── hardware_profiles.yaml # Hardware compatibility presets
├── data/                   # Data directories (documents, images, tables, KB)
├── outputs/                # Generated executive reports
├── logs/                   # System & security audit logs
├── tests/
│   ├── test_components.py  # Unit test suite
│   └── test_offline.py     # Sovereign air-gap end-to-end test
├── generate_demo_data.py   # Synthetic MRPL demo data generator
├── run.py                  # CLI launcher (python run.py)
└── requirements.txt        # Dependency manifest
```

---

## ⚡ Quick Start Instructions (Windows / VS Code)

### 1. Activate Environment & Install Dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Synthetic Demo Data
```powershell
python generate_demo_data.py
```

### 3. Run Automated Sovereign Air-Gap Tests
```powershell
python -m unittest tests/test_components.py
python tests/test_offline.py
```

### 4. Launch Industrial Workbench UI
```powershell
python run.py
```
Open your browser at `http://127.0.0.1:7860`.

---

## 🎬 SIH Internal Round Demo Flow (10 September 2026)

1. **Step 1**: Launch `python run.py`.
2. **Step 2**: Show **Hardware Specs & Model Router Decision** (e.g. RTX 3050 4GB / Tesla T4 / CPU Fallback mode).
3. **Step 3**: Select **"Golden Demo: Evidence-to-Action Agent"** tab and click **Execute Industrial Agent Workflow**.
4. **Step 4**: Highlight the visual **Agent Workflow Timeline** (Understand -> Plan -> Search Knowledge -> Analyze Multimodal -> Fuse -> Reason -> Risk -> Approval).
5. **Step 5**: Show **Local RAG Citations** (`sample_maintenance_sop.pdf — Page 12`).
6. **Step 6**: Show **Condition Reasoning & Risk Level (HIGH, 94.0% Confidence)**.
7. **Step 7**: Click **"✅ APPROVE RECOMMENDATION"** to trigger the **Human Approval Gate**.
8. **Step 8**: Download the generated **DOCX Executive Maintenance Report** from `outputs/`.
9. **Step 9**: Show the **Security & Air-Gap Audit** tab confirming `External API Requests: 0`.
