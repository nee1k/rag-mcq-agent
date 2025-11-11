"""Input validation utilities."""

from typing import Tuple

from ..config import MIN_CHOICES, MAX_CHOICES


def validate_question(question: str) -> Tuple[bool, str]:
    """
    Validate question input.
    
    Args:
        question: The question string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "Question cannot be empty"
    return True, ""


def validate_answer_choices(answer_choices: list) -> Tuple[bool, str]:
    """
    Validate answer choices input.
    
    Args:
        answer_choices: List of answer choice strings
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not answer_choices or len(answer_choices) < MIN_CHOICES:
        return False, f"Must provide at least {MIN_CHOICES} answer choices"
    if len(answer_choices) > MAX_CHOICES:
        return False, f"Maximum {MAX_CHOICES} answer choices supported"
    return True, ""

