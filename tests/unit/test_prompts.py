"""Unit tests for prompt formatting."""

import pytest
from agent.prompts import (
    format_answer_choices,
    format_context_section,
    format_web_search_section,
    PromptTemplates,
    FEW_SHOT_EXAMPLES
)


def test_format_answer_choices():
    """Test formatting answer choices."""
    choices = ["Option A", "Option B", "Option C", "Option D"]
    result = format_answer_choices(choices)
    assert "A) Option A" in result
    assert "B) Option B" in result
    assert "C) Option C" in result
    assert "D) Option D" in result


def test_format_context_section_empty():
    """Test formatting empty context section."""
    result = format_context_section([])
    assert result == ""


def test_format_context_section_with_chunks():
    """Test formatting context section with chunks."""
    chunks = [
        {"text": "This is context 1"},
        {"text": "This is context 2"}
    ]
    result = format_context_section(chunks, max_chunks=2)
    assert "[Context 1]" in result
    assert "This is context 1" in result
    assert "[Context 2]" in result
    assert "This is context 2" in result


def test_format_web_search_section_empty():
    """Test formatting empty web search section."""
    result = format_web_search_section([])
    assert result == ""


def test_format_web_search_section_with_results():
    """Test formatting web search section with results."""
    results = [
        {
            "title": "Test Article",
            "url": "https://example.com",
            "content": "This is test content"
        }
    ]
    result = format_web_search_section(results)
    assert "Test Article" in result
    assert "https://example.com" in result
    assert "This is test content" in result


def test_prompt_templates_loaded():
    """Test that prompt templates are loaded."""
    assert PromptTemplates.SYSTEM_ROLE
    assert PromptTemplates.CONTEXT_HEADER
    assert PromptTemplates.INSTRUCTIONS


def test_few_shot_examples_loaded():
    """Test that few-shot examples are loaded."""
    assert len(FEW_SHOT_EXAMPLES) > 0
    example = FEW_SHOT_EXAMPLES[0]
    assert "question" in example
    assert "choices" in example
    assert "answer" in example

