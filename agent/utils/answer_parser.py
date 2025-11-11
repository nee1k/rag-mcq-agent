"""Answer extraction and parsing utilities."""

import re
from typing import List


class AnswerParser:
    """Extract answers from model responses using multiple strategies."""
    
    # Chain-of-thought patterns for answer extraction
    COT_PATTERNS = [
        r'[Tt]herefore[,\s]+the\s+answer\s+is\s+([A-D])',
        r'[Aa]nswer:\s*([A-D])',
        r'[Cc]onclusion[:\s]+([A-D])',
        r'[Tt]he\s+correct\s+answer\s+is\s+([A-D])',
        r'[Aa]nswer\s+is\s+([A-D])',
    ]
    
    @staticmethod
    def extract_answer(response_text: str, answer_choices: List[str]) -> int:
        """
        Extract answer from response text using multiple parsing strategies.
        
        Args:
            response_text: The response text from the model
            answer_choices: List of answer choices
            
        Returns:
            Index of the answer choice (0-3) or -1 if not found
        """
        if not response_text or len(response_text.strip()) == 0:
            return -1
        
        # Strategy 1: CoT pattern matching (look for "Therefore", "Answer:", etc.)
        for pattern in AnswerParser.COT_PATTERNS:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                letter = match.group(1).upper()
                return ord(letter) - ord('A')
        
        # Strategy 2: Extract letter using regex (case-insensitive)
        letter_match = re.search(r'\b([A-D])\b', response_text, re.IGNORECASE)
        if letter_match:
            letter = letter_match.group(1).upper()
            return ord(letter) - ord('A')  # Convert A→0, B→1, C→2, D→3
        
        # Strategy 3: Extract number (0-3)
        number_match = re.search(r'\b([0-3])\b', response_text)
        if number_match:
            return int(number_match.group(1))
        
        # Strategy 4: Fuzzy match - search for substrings matching answer choices
        response_lower = response_text.lower()
        for i, answer_choice in enumerate(answer_choices):
            if answer_choice.lower() in response_lower:
                return i
        
        # If no match found, return -1
        return -1

