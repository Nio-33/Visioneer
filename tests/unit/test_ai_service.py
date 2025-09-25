"""
Unit tests for AI Service
"""

import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService

class TestAIService:
    """Test cases for AI Service"""
    
    def test_init_with_api_key(self):
        """Test AI service initialization with API key"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure') as mock_configure:
                with patch('google.generativeai.GenerativeModel') as mock_model:
                    service = AIService()
                    mock_configure.assert_called_once_with(api_key='test-key')
                    mock_model.assert_called_once_with('gemini-pro')
    
    def test_init_without_api_key(self):
        """Test AI service initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
                AIService()
    
    def test_generate_moodboard_concept_success(self):
        """Test successful moodboard concept generation"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model_class:
                    mock_model = Mock()
                    mock_model_class.return_value = mock_model
                    mock_response = Mock()
                    mock_response.text = "Generated concept"
                    mock_model.generate_content.return_value = mock_response
                    
                    service = AIService()
                    result = service.generate_moodboard_concept(
                        "Test story", "cinematic", 6, "16:9"
                    )
                    
                    assert result['status'] == 'success'
                    assert result['concept'] == "Generated concept"
                    mock_model.generate_content.assert_called_once()
    
    def test_generate_moodboard_concept_failure(self):
        """Test moodboard concept generation failure"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model_class:
                    mock_model = Mock()
                    mock_model_class.return_value = mock_model
                    mock_model.generate_content.side_effect = Exception("API Error")
                    
                    service = AIService()
                    result = service.generate_moodboard_concept(
                        "Test story", "cinematic", 6, "16:9"
                    )
                    
                    assert result['status'] == 'error'
                    assert 'API Error' in result['error']
    
    def test_refine_moodboard_concept_success(self):
        """Test successful moodboard concept refinement"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model_class:
                    mock_model = Mock()
                    mock_model_class.return_value = mock_model
                    mock_response = Mock()
                    mock_response.text = "Refined concept"
                    mock_model.generate_content.return_value = mock_response
                    
                    service = AIService()
                    result = service.refine_moodboard_concept(
                        "Original concept", "User feedback"
                    )
                    
                    assert result['status'] == 'success'
                    assert result['refined_concept'] == "Refined concept"
    
    def test_generate_image_prompts_success(self):
        """Test successful image prompt generation"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel') as mock_model_class:
                    mock_model = Mock()
                    mock_model_class.return_value = mock_model
                    mock_response = Mock()
                    mock_response.text = "Prompt 1\nPrompt 2\nPrompt 3"
                    mock_model.generate_content.return_value = mock_response
                    
                    service = AIService()
                    result = service.generate_image_prompts("Test concept", 3)
                    
                    assert len(result) == 3
                    assert all(isinstance(prompt, str) for prompt in result)
    
    def test_parse_image_prompts(self):
        """Test image prompt parsing"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel'):
                    service = AIService()
                    
                    # Test with numbered prompts
                    response_text = "1. First prompt\n2. Second prompt\n3. Third prompt"
                    result = service._parse_image_prompts(response_text, 3)
                    
                    assert len(result) == 3
                    assert "First prompt" in result[0]
                    assert "Second prompt" in result[1]
                    assert "Third prompt" in result[2]
    
    def test_create_moodboard_prompt(self):
        """Test moodboard prompt creation"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel'):
                    service = AIService()
                    
                    prompt = service._create_moodboard_prompt(
                        "Test story", "cinematic", 6, "16:9"
                    )
                    
                    assert "Test story" in prompt
                    assert "cinematic" in prompt
                    assert "6" in prompt
                    assert "16:9" in prompt
                    assert "VISUAL ELEMENTS" in prompt
                    assert "COLOR PALETTE" in prompt
