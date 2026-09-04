import sys
import os
import platform
import psutil
from typing import Dict, Any, Optional

class HardwareDetector:
    """Detects runtime system hardware including CPU, RAM, GPU, VRAM, and CUDA availability."""

    def __init__(self):
        self.cpu_name = platform.processor() or platform.machine() or "Generic CPU"
        self.cpu_cores_logical = psutil.cpu_count(logical=True) or 1
        self.cpu_cores_physical = psutil.cpu_count(logical=False) or 1
        self.total_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        
        self.cuda_available = False
        self.gpu_name = "N/A"
        self.gpu_vram_mb = 0
        self.gpu_vram_gb = 0.0
        self.gpu_count = 0
        self.detected_profile = "CPU_Only"

        self._detect_gpu()
        self._classify_profile()

    def _detect_gpu(self):
        """Attempts GPU detection via PyTorch if available, or system fallbacks."""
        try:
            import torch
            if torch.cuda.is_available():
                self.cuda_available = True
                self.gpu_count = torch.cuda.device_count()
                self.gpu_name = torch.cuda.get_device_name(0)
                # VRAM in MB
                vram_bytes = torch.cuda.get_device_properties(0).total_memory
                self.gpu_vram_mb = int(vram_bytes / (1024 ** 2))
                self.gpu_vram_gb = round(vram_bytes / (1024 ** 3), 2)
                return
        except Exception:
            pass

        # Fallback GPU detection check for Windows/Linux environment
        self.cuda_available = False
        self.gpu_name = "No CUDA GPU Detected"
        self.gpu_vram_mb = 0
        self.gpu_vram_gb = 0.0

    def _classify_profile(self):
        """Classifies hardware into one of the benchmark target profiles."""
        if not self.cuda_available or self.gpu_vram_mb < 1500:
            self.detected_profile = "CPU_Only"
        elif self.gpu_vram_mb >= 12000:
            self.detected_profile = "Tesla_T4"
        elif "3050" in self.gpu_name or (3000 <= self.gpu_vram_mb <= 4500):
            self.detected_profile = "RTX_3050"
        elif "P2000" in self.gpu_name or (4500 < self.gpu_vram_mb <= 6000):
            self.detected_profile = "Quadro_P2000"
        elif self.gpu_vram_mb > 6000:
            self.detected_profile = "Tesla_T4"
        else:
            self.detected_profile = "RTX_3050"

    def get_summary(self) -> Dict[str, Any]:
        """Returns hardware specs dictionary."""
        return {
            "platform": platform.platform(),
            "cpu": self.cpu_name,
            "cpu_logical_cores": self.cpu_cores_logical,
            "cpu_physical_cores": self.cpu_cores_physical,
            "ram_gb": self.total_ram_gb,
            "cuda_available": self.cuda_available,
            "gpu_name": self.gpu_name,
            "gpu_vram_mb": self.gpu_vram_mb,
            "gpu_vram_gb": self.gpu_vram_gb,
            "detected_profile": self.detected_profile,
        }

    def get_formatted_table(self) -> str:
        """Returns human-readable text table for UI/Logs."""
        return (
            f"=== RUNTIME HARDWARE SPECS ===\n"
            f"OS Platform     : {platform.platform()}\n"
            f"CPU             : {self.cpu_name} ({self.cpu_cores_logical} cores)\n"
            f"System RAM      : {self.total_ram_gb} GB\n"
            f"CUDA Available  : {'YES' if self.cuda_available else 'NO'}\n"
            f"GPU Model       : {self.gpu_name}\n"
            f"GPU VRAM        : {self.gpu_vram_gb} GB ({self.gpu_vram_mb} MB)\n"
            f"Target Profile  : {self.detected_profile}\n"
            f"==============================="
        )

# Global singleton instance
detector = HardwareDetector()
