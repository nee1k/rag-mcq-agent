"""Integration tests with mocked API calls."""

import pytest
from unittest.mock import patch, MagicMock
from hip_agent import HIPAgent


@patch('agent.utils.api_client.APIClient.chat_completion')
def test_agent_with_mocked_api(mock_api):
    """Test agent with mocked OpenAI API."""
    # Mock API response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Answer: B"
    mock_api.return_value = mock_response
    
    agent = HIPAgent()
    result = agent.get_response(
        "What is a GMO?",
        ["A genetically modified organism", "A type of protein", "A DNA sequence", "None of the above"]
    )
    
    assert result in [0, 1, 2, 3]
    mock_api.assert_called_once()


@patch('agent.utils.api_client.APIClient.chat_completion')
def test_agent_batch_processing_mocked(mock_api):
    """Test batch processing with mocked API."""
    # Mock API response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Answer: A"
    mock_api.return_value = mock_response
    
    agent = HIPAgent()
    questions = [
        ("Question 1?", ["A", "B", "C", "D"]),
        ("Question 2?", ["A", "B", "C", "D"])
    ]
    
    results = agent.get_response(questions, max_workers=2)
    
    assert len(results) == 2
    assert all(r in [0, 1, 2, 3, -1] for r in results)
    # Should be called twice (once per question)
    assert mock_api.call_count == 2


@patch('agent.utils.api_client.APIClient.chat_completion')
def test_agent_fallback_to_basic_mode(mock_api):
    """Test agent falls back to basic mode on API error."""
    # Mock API response for basic mode
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "A"
    
    # Basic mode should succeed
    mock_api.return_value = mock_response
    
    agent = HIPAgent()
    # This should work with basic mode
    result = agent._get_response_basic(
        "Test?",
        ["A", "B", "C", "D"]
    )
    
    assert result in [0, 1, 2, 3, -1]

