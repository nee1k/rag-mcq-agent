"""Unit tests for answer parser."""

import pytest
from agent.utils.answer_parser import AnswerParser


def test_extract_answer_from_letter_uppercase():
    """Test extracting answer from uppercase letter."""
    parser = AnswerParser()
    result = parser.extract_answer("The answer is B", ["A", "B", "C", "D"])
    assert result == 1


def test_extract_answer_from_letter_lowercase():
    """Test extracting answer from lowercase letter."""
    parser = AnswerParser()
    result = parser.extract_answer("Answer: c", ["A", "B", "C", "D"])
    assert result == 2


def test_extract_answer_from_number():
    """Test extracting answer from number."""
    parser = AnswerParser()
    result = parser.extract_answer("Answer: 2", ["A", "B", "C", "D"])
    assert result == 2


def test_extract_answer_cot_pattern():
    """Test extracting answer from chain-of-thought pattern."""
    parser = AnswerParser()
    result = parser.extract_answer(
        "Therefore, the answer is D",
        ["A", "B", "C", "D"]
    )
    assert result == 3


def test_extract_answer_fuzzy_match():
    """Test extracting answer using fuzzy matching."""
    parser = AnswerParser()
    result = parser.extract_answer(
        "I think it's a genetically modified organism",
        [
            "A genetically modified organism",
            "A type of protein",
            "A DNA sequence",
            "None of the above"
        ]
    )
    assert result == 0


def test_extract_answer_not_found():
    """Test when answer cannot be extracted."""
    parser = AnswerParser()
    result = parser.extract_answer("This doesn't contain an answer", ["A", "B", "C", "D"])
    assert result == -1


def test_extract_answer_empty_response():
    """Test with empty response."""
    parser = AnswerParser()
    result = parser.extract_answer("", ["A", "B", "C", "D"])
    assert result == -1


def test_extract_answer_whitespace_only():
    """Test with whitespace-only response."""
    parser = AnswerParser()
    result = parser.extract_answer("   ", ["A", "B", "C", "D"])
    assert result == -1

