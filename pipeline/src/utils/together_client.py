"""
Together AI client wrapper for LLM calls in the pipeline.

This module provides a unified interface for making LLM calls through Together AI,
replacing the existing Ollama-based implementations.
"""

import json
import time
from src.utils.logger import get_logger
from typing import Dict, List, Any, Optional
from together import Together


class TogetherAIClient:
    """
    Together AI client wrapper with retry logic and error handling.
    
    This class provides a consistent interface for making LLM calls through
    Together AI, with built-in retry logic, timeout handling, and response parsing.
    """
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.3, 
                 max_tokens: int = 2000, max_retries: int = 3, 
                 timeout_seconds: int = 120, retry_delay: float = 2.0):
        """
        Initialize Together AI client.
        
        Args:
            api_key: Together AI API key
            model: Model name (e.g., "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts
            timeout_seconds: Request timeout in seconds
            retry_delay: Delay between retries in seconds
        """
        self.client = Together(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.retry_delay = retry_delay
        self.logger = get_logger()
    
    def generate_completion(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Generate a completion using Together AI.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message for context
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If all retry attempts fail
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making Together AI request (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    self.logger.debug(f"Together AI response received ({len(content)} characters)")
                    self.logger.debug(f"Response content: {content[:200]}...")
                    return content
                else:
                    self.logger.error("No response choices received from Together AI")
                    self.logger.error(f"Full response: {response}")
                    raise Exception("No response content received from Together AI")
                    
            except Exception as e:
                self.logger.warning(f"Together AI request failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Together AI request failed after {self.max_retries} attempts: {e}")
    
    def generate_json_completion(self, prompt: str, system_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a JSON completion using Together AI.
        
        Args:
            prompt: The user prompt (should request JSON response)
            system_message: Optional system message for context
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            Exception: If JSON parsing fails or all retry attempts fail
        """
        response_text = self.generate_completion(prompt, system_message)
        
        try:
            # First try to parse the entire response as JSON
            try:
                self.logger.debug(f"Attempting to parse full response as JSON: {response_text[:200]}...")
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                self.logger.debug(f"Full response not valid JSON: {e}")
                pass
            
            # If that fails, try to extract JSON from response (in case there's extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                self.logger.error(f"No JSON found in Together AI response")
                self.logger.error(f"Raw response: {response_text}")
                raise ValueError("No JSON found in Together AI response")
            
            json_str = response_text[json_start:json_end]
            self.logger.debug(f"Extracted JSON: {json_str[:200]}...")
            
            return json.loads(json_str)
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse Together AI JSON response: {e}")
            self.logger.error(f"Raw response: {response_text}")
            raise Exception(f"Invalid JSON response from Together AI: {e}")
    
    def generate_batch_completions(self, prompts: List[str], system_message: Optional[str] = None) -> List[str]:
        """
        Generate multiple completions in batch.
        
        Args:
            prompts: List of user prompts
            system_message: Optional system message for context
            
        Returns:
            List of generated text responses
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                self.logger.debug(f"Processing batch item {i + 1}/{len(prompts)}")
                result = self.generate_completion(prompt, system_message)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch item {i + 1} failed: {e}")
                results.append("")  # Empty string as fallback
        
        return results


def create_together_client(config: Dict[str, Any]) -> TogetherAIClient:
    """
    Create a Together AI client from configuration.
    
    Args:
        config: Configuration dictionary with Together AI settings
        
    Returns:
        Configured TogetherAIClient instance
    """
    # Import here to avoid circular imports
    from src.utils.env_loader import EnvLoader
    
    # Get API key from environment
    env_loader = EnvLoader()
    api_key = env_loader.get_api_key('together_ai')
    
    if not api_key:
        raise ValueError(
            "Together AI API key not found. Please set TOGETHER_AI_API_KEY in your .env file."
        )
    
    return TogetherAIClient(
        api_key=api_key,
        model=config['model'],
        temperature=config.get('temperature', 0.3),
        max_tokens=config.get('max_tokens', 2000),
        max_retries=config.get('max_retries', 3),
        timeout_seconds=config.get('timeout_seconds', 120),
        retry_delay=config.get('retry_delay_seconds', 2.0)
    )
