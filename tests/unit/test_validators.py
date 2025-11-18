"""Unit tests for validators."""

import pytest
from agent.utils.validators import validate_question, validate_answer_choices


def test_validate_question_valid():
    """Test validation of valid questions."""
    valid, error = validate_question("What is DNA?")
    assert valid is True
    assert error == ""


def test_validate_question_empty():
    """Test validation of empty questions."""
    valid, error = validate_question("")
    assert valid is False
    assert "empty" in error.lower()


def test_validate_question_whitespace_only():
    """Test validation of whitespace-only questions."""
    valid, error = validate_question("   ")
    assert valid is False


def test_validate_answer_choices_valid():
    """Test validation of valid answer choices."""
    valid, error = validate_answer_choices(["A", "B", "C", "D"])
    assert valid is True
    assert error == ""


def test_validate_answer_choices_minimum():
    """Test validation with minimum number of choices."""
    valid, error = validate_answer_choices(["A", "B"])
    assert valid is True


def test_validate_answer_choices_too_few():
    """Test validation with too few choices."""
    valid, error = validate_answer_choices(["A"])
    assert valid is False
    assert "at least" in error.lower()


def test_validate_answer_choices_too_many():
    """Test validation with too many choices."""
    valid, error = validate_answer_choices(["A", "B", "C", "D", "E"])
    assert valid is False
    assert "maximum" in error.lower()


def test_validate_answer_choices_empty():
    """Test validation with empty list."""
    valid, error = validate_answer_choices([])
    assert valid is False

