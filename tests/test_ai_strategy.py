
import pytest
from unittest.mock import MagicMock, patch
from src.services.ai.clients import GeminiProClient, GeminiFlashClient
from src.services.ai.factory import ModelFactory

@patch('src.services.ai.clients.genai')
def test_gemini_pro_client(mock_genai):
    """Test functionality of GeminiProClient."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Generated Content"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    client = GeminiProClient(api_key="fake_key")
    result = client.generate("Test Prompt")
    
    assert result == "Generated Content"
    mock_model.generate_content.assert_called_once_with("Test Prompt")

@patch('src.services.ai.clients.genai')
def test_gemini_flash_truncation(mock_genai):
    """Test that Flash client truncates long prompts."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Ok"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    # Simulate count_tokens returning high value
    mock_model.count_tokens.return_value.total_tokens = 10000 
    
    client = GeminiFlashClient(api_key="fake_key")
    client.token_limit = 5000 # Force limit
    
    long_prompt = "A" * 20000
    client.generate(long_prompt)
    
    # Check if prompt passed to generate_content was truncated
    args, _ = mock_model.generate_content.call_args
    sent_prompt = args[0]
    
    assert "TRUNCATED" in sent_prompt
    assert len(sent_prompt) < 20000 + 100 # Should be around limit*4

def test_factory_returns_correct_client():
    from src.config.settings import settings
    
    # Mock settings
    with patch.object(settings, 'AI_MODEL_TYPE', 'flash'):
        with patch.object(settings, 'GOOGLE_API_KEY', 'key'):
             # We need to mock genai constructor too to avoid real network call
             with patch('src.services.ai.clients.genai'):
                 client = ModelFactory.create_client()
                 assert isinstance(client, GeminiFlashClient)
    
    with patch.object(settings, 'AI_MODEL_TYPE', 'pro'):
        with patch.object(settings, 'GOOGLE_API_KEY', 'key'):
             with patch('src.services.ai.clients.genai'):
                 client = ModelFactory.create_client()
                 assert isinstance(client, GeminiProClient)
