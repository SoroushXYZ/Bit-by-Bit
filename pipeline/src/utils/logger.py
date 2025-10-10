"""
Logging utility for the Bit-by-Bit newsletter pipeline.
Provides centralized logging with rotation and graceful error handling.
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class PipelineLogger:
    """Centralized logging system for the pipeline."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the logger with file rotation and console output."""
        logger = logging.getLogger('pipeline')
        logger.setLevel(getattr(logging, self.config['level']))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(self.config['format'])
        
        # File handler with rotation
        log_file = self.config['file']
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config['max_size_mb'] * 1024 * 1024,
            backupCount=self.config['backup_count']
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """Log error message with optional exception details."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """Log critical message that might break the pipeline."""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)


def load_logger_config(config_path: str) -> PipelineLogger:
    """Load logger configuration and create logger instance."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return PipelineLogger(config['logging'])
    except Exception as e:
        # Fallback logger if config loading fails; honor run-scoped logging if available
        run_id = os.getenv('BITBYBIT_RUN_ID')
        fallback_file = f"data/{run_id}/logs/pipeline.log" if run_id else 'logs/pipeline.log'
        fallback_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': fallback_file,
            'max_size_mb': 100,
            'backup_count': 5
        }
        return PipelineLogger(fallback_config)


# Global logger instance
_logger: Optional[PipelineLogger] = None


def get_logger() -> PipelineLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        # If no logger has been initialized, create a temporary one
        # Prefer run-scoped path if BITBYBIT_RUN_ID is set
        run_id = os.getenv('BITBYBIT_RUN_ID')
        fallback_file = f"data/{run_id}/logs/pipeline.log" if run_id else 'logs/pipeline.log'
        fallback_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': fallback_file,
            'max_size_mb': 100,
            'backup_count': 5
        }
        _logger = PipelineLogger(fallback_config)
    return _logger


def initialize_logger(config_path: str, run_id: str = None) -> PipelineLogger:
    """Initialize the global logger with config and optional run-scoped directory."""
    global _logger
    
    # Load base config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging_config = config['logging'].copy()
        
        # If run_id is provided, update log file path to be run-scoped
        if run_id:
            original_log_file = logging_config['file']
            # Convert logs/pipeline.log to data/<run_id>/logs/pipeline.log
            log_filename = os.path.basename(original_log_file)
            logging_config['file'] = f"data/{run_id}/logs/{log_filename}"
        
        _logger = PipelineLogger(logging_config)
    except Exception as e:
        # Fallback logger if config loading fails
        fallback_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': f"data/{run_id}/logs/pipeline.log" if run_id else 'logs/pipeline.log',
            'max_size_mb': 100,
            'backup_count': 5
        }
        _logger = PipelineLogger(fallback_config)
    
    return _logger


def reset_logger() -> None:
    """Reset the global logger instance to force reinitialization."""
    global _logger
    if _logger is not None:
        # Close existing handlers to avoid file locks
        for handler in _logger.logger.handlers[:]:
            handler.close()
            _logger.logger.removeHandler(handler)
    _logger = None
