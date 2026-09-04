import logging
import datetime
from pathlib import Path
from app.config import config

class AuditLogger:
    """Manages structured file logs for agent, security, router, and audit events."""

    def __init__(self):
        self.log_dir = config.log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.agent_log_path = self.log_dir / "agent.log"
        self.security_log_path = self.log_dir / "security.log"
        self.router_log_path = self.log_dir / "model_router.log"
        self.audit_log_path = self.log_dir / "audit.log"

    def log_event(self, log_name: str, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target_path = self.log_dir / f"{log_name}.log"
        with open(target_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

audit_logger = AuditLogger()
