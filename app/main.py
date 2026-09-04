import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import config
from app.ui import create_ui
from models.hardware import detector
from security.policy import security_policy
from generate_demo_data import create_synthetic_demo_files

def main():
    print("==========================================================")
    print(" MRPL SOVEREIGN ON-PREMISE AGENTIC AI WORKBENCH (SIH26117)")
    print("==========================================================")
    
    # 1. Enforce air-gap security policy
    security_policy.enforce_policy()
    print("✓ Air-gap security policy enforced (0 external calls allowed).")

    # 2. Print hardware detection summary
    print(detector.get_formatted_table())

    # 3. Ensure synthetic demo data exists
    create_synthetic_demo_files()

    # 4. Launch Gradio UI
    demo = create_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)

if __name__ == "__main__":
    main()
