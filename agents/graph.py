import logging
from typing import Dict, Any, List, Optional
from agents.state import AgentState
from agents.nodes import (
    understand_task_node,
    plan_node,
    collect_inputs_node,
    search_knowledge_node,
    analyze_multimodal_node,
    fuse_evidence_node,
    reason_node,
    assess_risk_node,
    generate_report_node,
)

logger = logging.getLogger(__name__)

class IndustrialAgentGraph:
    """State Machine Agent Graph Runner."""

    def __init__(self):
        self._build_graph()

    def _build_graph(self):
        """Attempts compiling with langgraph, or provides direct fallback runner."""
        try:
            from langgraph.graph import StateGraph, END
            workflow = StateGraph(AgentState)

            workflow.add_node("understand_task", understand_task_node)
            workflow.add_node("plan", plan_node)
            workflow.add_node("collect_inputs", collect_inputs_node)
            workflow.add_node("search_knowledge", search_knowledge_node)
            workflow.add_node("analyze_multimodal", analyze_multimodal_node)
            workflow.add_node("fuse_evidence", fuse_evidence_node)
            workflow.add_node("reason", reason_node)
            workflow.add_node("assess_risk", assess_risk_node)
            workflow.add_node("generate_report", generate_report_node)

            workflow.set_entry_point("understand_task")

            workflow.add_edge("understand_task", "plan")
            workflow.add_edge("plan", "collect_inputs")
            workflow.add_edge("collect_inputs", "search_knowledge")
            workflow.add_edge("search_knowledge", "analyze_multimodal")
            workflow.add_edge("analyze_multimodal", "fuse_evidence")
            workflow.add_edge("fuse_evidence", "reason")
            workflow.add_edge("reason", "assess_risk")
            workflow.add_edge("assess_risk", "generate_report")
            workflow.add_edge("generate_report", END)

            self.app = workflow.compile()
            self.use_langgraph = True
        except Exception as e:
            logger.warning(f"LangGraph compile warning: {e}. Utilizing lightweight local state runner.")
            self.use_langgraph = False

    def run(self, initial_state: AgentState) -> AgentState:
        """Executes full agent workflow graph."""
        if getattr(self, "use_langgraph", False):
            try:
                return self.app.invoke(initial_state)
            except Exception as ex:
                logger.warning(f"LangGraph invoke error: {ex}. Running fallback node execution.")

        # Fallback sequential state runner
        s = dict(initial_state)
        s.update(understand_task_node(s))
        s.update(plan_node(s))
        s.update(collect_inputs_node(s))
        s.update(search_knowledge_node(s))
        s.update(analyze_multimodal_node(s))
        s.update(fuse_evidence_node(s))
        s.update(reason_node(s))
        s.update(assess_risk_node(s))
        s.update(generate_report_node(s))
        return s

agent_graph = IndustrialAgentGraph()
