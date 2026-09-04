import logging
from typing import Dict, Any, Tuple
from models.hardware import detector, HardwareDetector
from models.registry import registry, ModelRegistry
from models.base_model import BaseModelProvider, OllamaProvider, LocalFallbackProvider, TransformersProvider

logger = logging.getLogger(__name__)

class ModelRouter:
    """Hardware and Task-Aware local model router."""

    def __init__(self, hw_detector: HardwareDetector = detector, mod_registry: ModelRegistry = registry):
        self.detector = hw_detector
        self.registry = mod_registry

    def route(self, task_type: str) -> Tuple[BaseModelProvider, Dict[str, Any]]:
        """
        Determines the optimal model provider and routing metadata for a task request.
        
        Task Types:
        - TEXT_REASONING
        - DOCUMENT_ANALYSIS
        - RAG
        - CODING
        - VISION
        - MULTIMODAL
        - SMALL_CLASSIFICATION
        """
        hw_info = self.detector.get_summary()
        available_vram_mb = hw_info["gpu_vram_mb"]
        profile_name = hw_info["detected_profile"]

        # Default fallback provider instance
        fallback_provider = LocalFallbackProvider()

        # Check if Ollama is running locally
        test_ollama = OllamaProvider("test")
        ollama_active = test_ollama.is_available()

        # Select target model spec based on task type
        model_key = "text_reasoning_fast"
        if task_type in ["CODING"]:
            model_key = "coding_expert"
        elif task_type in ["VISION", "MULTIMODAL"]:
            model_key = "vision_multimodal"
        elif task_type in ["DOCUMENT_ANALYSIS", "RAG"]:
            model_key = "text_reasoning_standard"

        model_spec = self.registry.get_model(model_key) or self.registry.get_model("text_reasoning_fast")
        
        # Determine routing decision
        selected_model_name = "sovereign_rule_engine"
        selected_provider_type = "local_fallback"
        quantization = "N/A"
        fallback_mode_active = False
        fallback_reason = ""
        context_length = 4096

        if not ollama_active:
            fallback_mode_active = True
            fallback_reason = "Local Ollama service not running or unreachable. Using Sovereign Local Fallback Engine."
            provider = fallback_provider
            selected_model_name = "sovereign_rule_engine"
        else:
            req_vram = model_spec.get("minimum_vram_mb", 2048) if model_spec else 2048
            if available_vram_mb < req_vram:
                # VRAM insufficient for requested model, check fallback model or smaller model
                fallback_model_key = model_spec.get("fallback_model") if model_spec else "llama3.2:1b"
                if fallback_model_key and fallback_model_key != "ocr_image_extractor":
                    selected_model_name = fallback_model_key
                    selected_provider_type = "ollama"
                    provider = OllamaProvider(selected_model_name)
                    quantization = "Q4_K_S (Reduced VRAM)"
                    fallback_mode_active = True
                    fallback_reason = f"VRAM ({available_vram_mb} MB) below required ({req_vram} MB). Downgraded to {selected_model_name}."
                else:
                    provider = fallback_provider
                    selected_model_name = "sovereign_rule_engine"
                    fallback_mode_active = True
                    fallback_reason = f"VRAM ({available_vram_mb} MB) insufficient for model {model_key}. Switched to local rule fallback."
            else:
                selected_model_name = model_spec.get("name", "llama3.2:1b")
                selected_provider_type = "ollama"
                quantization = model_spec.get("quantization", "Q4_K_M")
                context_length = model_spec.get("context_length", 4096)
                provider = OllamaProvider(selected_model_name)
                fallback_reason = "Optimal hardware match found."

        routing_metadata = {
            "task_type": task_type,
            "selected_model": selected_model_name,
            "provider_type": selected_provider_type,
            "quantization": quantization,
            "context_length": context_length,
            "detected_profile": profile_name,
            "available_vram_mb": available_vram_mb,
            "fallback_mode_active": fallback_mode_active,
            "fallback_reason": fallback_reason,
            "ollama_active": ollama_active,
        }

        logger.info(f"Model Router decision for [{task_type}]: {routing_metadata}")
        return provider, routing_metadata

router = ModelRouter()
