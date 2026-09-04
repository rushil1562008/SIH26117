import sys
import os
import ast
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

class SandboxedCodeExecutor:
    """Executes generated Python code inside an isolated temporary directory with timeouts and safety checks."""

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds

    def _verify_ast_safety(self, code_str: str) -> Tuple[bool, str]:
        """Performs static analysis to reject destructive OS calls."""
        try:
            tree = ast.parse(code_str)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["shutil", "socket", "urllib", "http", "ftplib"]:
                            return False, f"Forbidden import module: '{alias.name}'"
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ["shutil", "socket", "urllib", "http", "ftplib"]:
                        return False, f"Forbidden import from module: '{node.module}'"
            return True, "AST verification passed."
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"

    def execute_python(self, code_str: str) -> Dict[str, Any]:
        """Executes code in isolated temporary directory."""
        is_safe, safety_msg = self._verify_ast_safety(code_str)
        if not is_safe:
            return {
                "success": False,
                "status": "REJECTED_BY_SANDBOX_POLICY",
                "stdout": "",
                "stderr": safety_msg,
                "exit_code": -1,
                "code": code_str,
            }

        with tempfile.TemporaryDirectory(prefix="sih_sandbox_") as tmpdir:
            script_path = Path(tmpdir) / "sandbox_script.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code_str)

            try:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
                return {
                    "success": result.returncode == 0,
                    "status": "COMPLETED" if result.returncode == 0 else "EXECUTION_ERROR",
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "exit_code": result.returncode,
                    "code": code_str,
                    "sandbox_dir": tmpdir,
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "status": "TIMEOUT_EXCEEDED",
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.timeout_seconds} seconds.",
                    "exit_code": -1,
                    "code": code_str,
                }
            except Exception as e:
                return {
                    "success": False,
                    "status": "SYSTEM_ERROR",
                    "stdout": "",
                    "stderr": str(e),
                    "exit_code": -1,
                    "code": code_str,
                }

code_executor = SandboxedCodeExecutor()
