"""
Configuration loader utility for the Bit-by-Bit newsletter pipeline.
Handles loading and validation of JSON configuration files.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ConfigLoader:
    """Utility class for loading and managing pipeline configurations."""
    
    def __init__(self, base_config_path: str = "config/pipeline_config.json", 
                 global_config_path: str = "config/global_config.json"):
        self.base_config_path = base_config_path
        self.global_config_path = global_config_path
        self.base_config = self._load_config(base_config_path)
        self.global_config = self._load_global_config()
        # Establish a per-run identifier and directories
        self.run_id = os.getenv('BITBYBIT_RUN_ID') or datetime.now().strftime('%Y%m%d_%H%M%S')
        self._data_paths = self._compute_run_scoped_paths()
        self._ensure_directories()
    
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
    
    def _load_global_config(self) -> Dict[str, Any]:
        """Load global configuration file with error handling."""
        try:
            if not os.path.exists(self.global_config_path):
                # Return empty dict if global config doesn't exist
                return {}
            
            with open(self.global_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in global configuration file {self.global_config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load global configuration from {self.global_config_path}: {e}")
    
    def _merge_global_config(self, step_config: Dict[str, Any], step_name: str) -> Dict[str, Any]:
        """Merge global configuration with step-specific configuration."""
        if not self.global_config:
            return step_config
        
        # Create a deep copy of step config to avoid modifying original
        merged_config = self._deep_merge({}, step_config)
        
        # Merge global settings based on step name
        global_settings = self.global_config.get('global', {})
        
        # Merge LLM settings if step uses LLM
        if step_name in ['llm_quality_scoring', 'article_prioritization', 'summarization']:
            llm_default = self.global_config.get('llm', {}).get('default', {})
            llm_specific = self.global_config.get('llm', {}).get(step_name, {})
            
            # Merge LLM config into step config
            if 'llm' not in merged_config:
                merged_config['llm'] = {}
            
            # Apply default LLM settings first, then step-specific overrides
            merged_config['llm'] = self._deep_merge(llm_default, merged_config['llm'])
            merged_config['llm'] = self._deep_merge(merged_config['llm'], llm_specific)
        
        # Merge output settings
        output_default = self.global_config.get('output', {}).get('default', {})
        if 'output' in merged_config:
            merged_config['output'] = self._deep_merge(output_default, merged_config['output'])
        
        # Merge error handling settings
        error_default = self.global_config.get('error_handling', {}).get('default', {})
        error_specific = self.global_config.get('error_handling', {}).get(step_name, {})
        if 'error_handling' in merged_config:
            merged_config['error_handling'] = self._deep_merge(error_default, merged_config['error_handling'])
            merged_config['error_handling'] = self._deep_merge(merged_config['error_handling'], error_specific)
        
        # Merge logging settings
        logging_default = self.global_config.get('logging', {}).get('default', {})
        logging_specific = self.global_config.get('logging', {}).get(step_name, {})
        if 'logging' in merged_config:
            merged_config['logging'] = self._deep_merge(logging_default, merged_config['logging'])
            merged_config['logging'] = self._deep_merge(merged_config['logging'], logging_specific)
        
        # Merge text processing settings
        text_default = self.global_config.get('text_processing', {}).get('default', {})
        if 'text_processing' in merged_config:
            merged_config['text_processing'] = self._deep_merge(text_default, merged_config['text_processing'])
        elif step_name in ['llm_quality_scoring', 'summarization', 'deduplication']:
            # Add text processing config for steps that need it
            merged_config['text_processing'] = text_default
        
        # Merge performance settings
        perf_default = self.global_config.get('performance', {}).get('default', {})
        perf_specific = self.global_config.get('performance', {}).get(step_name, {})
        if 'performance' in merged_config:
            merged_config['performance'] = self._deep_merge(perf_default, merged_config['performance'])
            merged_config['performance'] = self._deep_merge(merged_config['performance'], perf_specific)
        
        # Merge quality settings for quality scoring step
        if step_name == 'llm_quality_scoring':
            quality_levels = self.global_config.get('quality', {}).get('levels', {})
            quality_criteria = self.global_config.get('quality', {}).get('criteria', {})
            if 'quality_levels' not in merged_config and quality_levels:
                merged_config['quality_levels'] = quality_levels
            if 'quality_criteria' not in merged_config and quality_criteria:
                merged_config['quality_criteria'] = quality_criteria
        
        # Merge fallback strategy settings
        fallback_default = self.global_config.get('fallback_strategy', {}).get('default', {})
        fallback_specific = self.global_config.get('fallback_strategy', {}).get(step_name, {})
        if 'fallback_strategy' in merged_config:
            merged_config['fallback_strategy'] = self._deep_merge(fallback_default, merged_config['fallback_strategy'])
            merged_config['fallback_strategy'] = self._deep_merge(merged_config['fallback_strategy'], fallback_specific)
        
        return merged_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override values taking precedence."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pipeline step with global config merging."""
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
            # Merge with global configuration
            merged_config = self._merge_global_config(step_config, step_name)
            return merged_config
        else:
            # Return basic step info if no specific config file
            return step_info
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get the main pipeline configuration."""
        return self.base_config
    
    def get_data_paths(self) -> Dict[str, str]:
        """Get per-run data directory paths (data/<run_id>/{raw,processed,output})."""
        return self._data_paths

    def get_run_id(self) -> str:
        """Return the current pipeline run identifier."""
        return self.run_id

    def _compute_run_scoped_paths(self) -> Dict[str, str]:
        """Compute run-scoped data directories based on config and run_id."""
        data_config = self.base_config.get('data', {})
        base_root = Path(data_config.get('base_path', 'data'))
        run_root = base_root / self.run_id
        return {
            'base': str(run_root),
            'raw': str(run_root / 'raw'),
            'processed': str(run_root / 'processed'),
            'output': str(run_root / 'output'),
            'logs': str(run_root / 'logs')
        }

    def _ensure_directories(self) -> None:
        """Create run-scoped directories if they do not exist."""
        for key in ['base', 'raw', 'processed', 'output', 'logs']:
            path = Path(self._data_paths[key])
            path.mkdir(parents=True, exist_ok=True)
    
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
