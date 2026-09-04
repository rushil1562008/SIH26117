from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    """LangGraph workflow state schema for Evidence-to-Action Industrial Agent."""
    
    task_description: str
    task_type: str
    pdf_path: Optional[str]
    image_path: Optional[str]
    excel_path: Optional[str]
    
    plan: List[str]
    raw_evidence: Dict[str, Any]
    rag_citations: List[Dict[str, Any]]
    fused_evidence: str
    reasoning_output: str
    
    risk_level: str
    confidence_score: float
    recommendation: str
    
    human_approval_status: str  # "PENDING", "APPROVED", "MODIFIED", "REJECTED"
    approver_notes: str
    generated_report_path: Optional[str]
    
    execution_logs: List[str]
    current_step: str
    model_routing_info: Dict[str, Any]
