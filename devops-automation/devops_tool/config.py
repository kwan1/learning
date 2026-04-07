"""Configuration management using pathlib and YAML."""
from pathlib import Path
from typing import Any
import yaml


class Config:
    """Handles loading and accessing configuration from YAML file."""
    
    def __init__(self, config_path: Path | str | None = None):
        """Initialize config with optional path to config.yaml.
        
        Args:
            config_path: Path to config file. If None, looks for config.yaml in current dir.
        """
        if config_path is None:
            # Use pathlib to find config.yaml in project root
            self.config_path = Path.cwd() / "config.yaml"
        else:
            self.config_path = Path(config_path)
        
        self.data: dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with self.config_path.open("r") as f:
            self.data = yaml.safe_load(f) or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'app.name').
        
        Args:
            key: Config key in dot notation (e.g., 'logging.level')
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        keys = key.split(".")
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_path(self, key: str) -> Path:
        """Get a config value as a Path object.
        
        Args:
            key: Config key
            
        Returns:
            Path object
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"Path config '{key}' not found")
        return Path(value)
