import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import config

class ModelRegistry:
    """Manages system model specifications and hardware profile presets."""

    def __init__(self, models_yaml_path: Optional[Path] = None, profiles_yaml_path: Optional[Path] = None):
        self.models_yaml_path = models_yaml_path or (config.config_dir / "models.yaml")
        self.profiles_yaml_path = profiles_yaml_path or (config.config_dir / "hardware_profiles.yaml")
        
        self.models: Dict[str, Any] = {}
        self.profiles: Dict[str, Any] = {}
        
        self.reload()

    def reload(self):
        """Loads or reloads YAML configuration files."""
        if self.models_yaml_path.exists():
            with open(self.models_yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.models = data.get("models", {})
        else:
            self.models = {}

        if self.profiles_yaml_path.exists():
            with open(self.profiles_yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self.profiles = data.get("profiles", {})
        else:
            self.profiles = {}

    def get_model(self, key: str) -> Optional[Dict[str, Any]]:
        return self.models.get(key)

    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        return self.profiles.get(profile_name)

registry = ModelRegistry()
