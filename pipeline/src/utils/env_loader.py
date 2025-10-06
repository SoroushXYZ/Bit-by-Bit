"""
Environment Variables Loader

Handles loading API keys and sensitive configuration from environment files.
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

from src.utils.logger import get_logger


class EnvLoader:
    """Loads environment variables from .env files."""
    
    def __init__(self, env_file_path: Optional[str] = None):
        """
        Initialize the environment loader.
        
        Args:
            env_file_path: Path to the .env file. If None, looks for api_keys.env in config/
        """
        self.logger = get_logger()
        
        if env_file_path is None:
            # Default to .env in pipeline directory
            pipeline_dir = Path(__file__).parent.parent.parent
            env_file_path = pipeline_dir / '.env'
        
        self.env_file_path = Path(env_file_path)
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from the .env file."""
        if self.env_file_path.exists():
            load_dotenv(self.env_file_path)
            self.logger.info(f"Loaded environment variables from: {self.env_file_path}")
        else:
            self.logger.warning(f"Environment file not found: {self.env_file_path}")
            self.logger.info("Using system environment variables only")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a specific service.
        
        Args:
            service: Service name (e.g., 'finnhub', 'alpha_vantage')
            
        Returns:
            API key string or None if not found
        """
        key_mapping = {
            'together_ai': 'TOGETHER_AI_API_KEY',
            'finnhub': 'FINNHUB_API_KEY',
            'alpha_vantage': 'ALPHA_VANTAGE_API_KEY', 
            'polygon': 'POLYGON_API_KEY',
            'yahoo_finance': 'YAHOO_FINANCE_ENABLED'
        }
        
        env_var = key_mapping.get(service.lower())
        if not env_var:
            self.logger.error(f"Unknown service: {service}")
            return None
        
        api_key = os.getenv(env_var)
        if not api_key:
            self.logger.warning(f"API key not found for {service} (env var: {env_var})")
            return None
        
        # Mask the key for logging
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        self.logger.info(f"API key loaded for {service}: {masked_key}")
        
        return api_key
    
    def get_all_api_keys(self) -> Dict[str, Optional[str]]:
        """
        Get all available API keys.
        
        Returns:
            Dictionary mapping service names to API keys
        """
        services = ['together_ai', 'finnhub', 'alpha_vantage', 'polygon', 'yahoo_finance']
        return {service: self.get_api_key(service) for service in services}
    
    def is_service_available(self, service: str) -> bool:
        """
        Check if a service is available (has API key).
        
        Args:
            service: Service name
            
        Returns:
            True if service is available, False otherwise
        """
        api_key = self.get_api_key(service)
        return api_key is not None and api_key != "your_api_key_here"
