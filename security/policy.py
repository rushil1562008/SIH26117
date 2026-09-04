import os
from app.config import config

class SovereignSecurityPolicy:
    """Enforces strict air-gap compliance and blocks cloud API keys."""

    def __init__(self):
        self.enforce_policy()

    def enforce_policy(self):
        """Verifies that no cloud API keys are active in environment variables."""
        forbidden_keys = [
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
            "AZURE_OPENAI_KEY",
            "AWS_SECRET_ACCESS_KEY",
        ]
        active_cloud_keys = [k for k in forbidden_keys if os.environ.get(k)]
        if active_cloud_keys:
            raise SecurityError(f"Cloud API keys detected in environment: {active_cloud_keys}. Air-gapped sovereign policy forbids cloud credentials.")

class SecurityError(Exception):
    pass

security_policy = SovereignSecurityPolicy()
