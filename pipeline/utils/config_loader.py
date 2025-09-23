"""
Configuration loader utility for the Bit-by-Bit newsletter pipeline.
Handles loading and validation of JSON configuration files.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Utility class for loading and managing pipeline configurations."""
    
    def __init__(self, base_config_path: str = "pipeline/config/pipeline_config.json"):
        self.base_config_path = base_config_path
        self.base_config = self._load_config(base_config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load JSON configuration file with error handling."""
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file {config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {config_path}: {e}")
    
    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pipeline step."""
        if 'steps' not in self.base_config:
            raise ValueError("No steps configuration found in base config")
        
        if step_name not in self.base_config['steps']:
            raise ValueError(f"Step '{step_name}' not found in configuration")
        
        step_info = self.base_config['steps'][step_name]
        
        if not step_info.get('enabled', False):
            raise ValueError(f"Step '{step_name}' is disabled in configuration")
        
        # Load step-specific configuration
        config_file = step_info.get('config_file')
        if config_file and os.path.exists(config_file):
            step_config = self._load_config(config_file)
            return step_config
        else:
            # Return basic step info if no specific config file
            return step_info
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get the main pipeline configuration."""
        return self.base_config
    
    def get_data_paths(self) -> Dict[str, str]:
        """Get data directory paths from configuration."""
        data_config = self.base_config.get('data', {})
        return {
            'base': data_config.get('base_path', 'pipeline/data'),
            'raw': data_config.get('raw_data_path', 'pipeline/data/raw'),
            'processed': data_config.get('processed_data_path', 'pipeline/data/processed'),
            'output': data_config.get('output_data_path', 'pipeline/data/output')
        }
    
    def validate_step_config(self, step_config: Dict[str, Any], required_fields: list) -> bool:
        """Validate that step configuration has required fields."""
        missing_fields = []
        for field in required_fields:
            if field not in step_config:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {missing_fields}")
        
        return True
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'logging.level')."""
        keys = key_path.split('.')
        value = self.base_config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default


def load_pipeline_config(config_path: str = "pipeline/config/pipeline_config.json") -> ConfigLoader:
    """Load pipeline configuration and return ConfigLoader instance."""
    return ConfigLoader(config_path)
