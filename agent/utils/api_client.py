"""OpenAI API client with retry logic."""

from openai import OpenAI, RateLimitError, APIError, APIConnectionError
import time
import random
from typing import Callable

from ..config import API_MAX_RETRIES, OPENAI_MODEL


class APIClient:
    """OpenAI API client with retry logic."""
    
    def __init__(self, api_key: str):
        """
        Initialize API client.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.model = OPENAI_MODEL
    
    def call_with_retry(self, api_call_func: Callable, max_retries: int = API_MAX_RETRIES):
        """
        Execute API call with exponential backoff retry logic.
        
        Args:
            api_call_func: Function that makes the API call
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response
            
        Raises:
            Exception: If max retries exceeded
        """
        for attempt in range(max_retries):
            try:
                return api_call_func()
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit. Waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
            except APIError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt)
                print(f"API error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            except APIConnectionError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 5 * (attempt + 1)
                print(f"Service unavailable. Waiting {wait_time}s...")
                time.sleep(wait_time)
        raise Exception("Max retries exceeded")
    
    def chat_completion(self, prompt: str):
        """
        Make a chat completion API call.
        
        Args:
            prompt: The prompt text
            
        Returns:
            API response
        """
        return self.call_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
        )

