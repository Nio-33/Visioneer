"""
Unit tests for AI service
"""

import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService

class TestAIService:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.ai_service = AIService()
        self.sample_story = """
        A cyberpunk thriller set in Neo-Tokyo 2087. Neon-lit streets, 
        rain-soaked pavement, towering holographic advertisements.
        """
    
    def test_initialization(self):
        """Test AI service initialization"""
        assert not self.ai_service.initialized
        assert self.ai_service.model is None
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_initialize_success(self, mock_model, mock_configure):
        """Test successful AI service initialization"""
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        result = self.ai_service.initialize('test-api-key')
        
        mock_configure.assert_called_once_with(api_key='test-api-key')
        mock_model.assert_called_once_with('gemini-pro')
        assert self.ai_service.initialized
        assert self.ai_service.model == mock_model_instance
    
    def test_initialize_without_api_key(self):
        """Test initialization without API key"""
        with pytest.raises(Exception):
            self.ai_service.initialize(None)
    
    def test_analyze_story_not_initialized(self):
        """Test story analysis when service not initialized"""
        with pytest.raises(Exception, match="AI service not initialized"):
            self.ai_service.analyze_story(self.sample_story)
    
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_story_success(self, mock_model):
        """Test successful story analysis"""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = """
        {
            "setting": ["Neo-Tokyo", "cyberpunk city"],
            "time_period": "2087",
            "mood": ["dark", "futuristic", "mysterious"],
            "colors": ["neon", "dark", "blue"],
            "lighting": "neon lighting",
            "characters": ["tech detective"],
            "visual_elements": ["holograms", "rain"],
            "genre": "cyberpunk"
        }
        """
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        # Initialize service
        self.ai_service.model = mock_model_instance
        self.ai_service.initialized = True
        
        # Test analysis
        result = self.ai_service.analyze_story(self.sample_story, 'cinematic')
        
        assert result['success']
        assert 'analysis' in result
        assert result['analysis']['setting'] == ["Neo-Tokyo", "cyberpunk city"]
        assert result['analysis']['genre'] == "cyberpunk"
    
    @patch('google.generativeai.GenerativeModel')
    def test_analyze_story_failure(self, mock_model):
        """Test story analysis failure"""
        mock_model_instance = Mock()
        mock_model_instance.generate_content.side_effect = Exception("API Error")
        mock_model.return_value = mock_model_instance
        
        self.ai_service.model = mock_model_instance
        self.ai_service.initialized = True
        
        result = self.ai_service.analyze_story(self.sample_story)
        
        assert not result['success']
        assert 'error' in result
        assert result['analysis'] is None
    
    @patch('google.generativeai.GenerativeModel')
    def test_generate_image_prompts_success(self, mock_model):
        """Test successful image prompt generation"""
        mock_response = Mock()
        mock_response.text = '["prompt1", "prompt2", "prompt3"]'
        
        mock_model_instance = Mock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        self.ai_service.model = mock_model_instance
        self.ai_service.initialized = True
        
        analysis = {"setting": ["Neo-Tokyo"], "mood": ["dark"]}
        result = self.ai_service.generate_image_prompts(analysis, 3)
        
        assert result == ["prompt1", "prompt2", "prompt3"]
    
    def test_fallback_parse_analysis(self):
        """Test fallback analysis parsing"""
        response_text = "Invalid JSON response"
        result = self.ai_service._fallback_parse_analysis(response_text)
        
        assert result["setting"] == ["Unknown location"]
        assert result["mood"] == ["mysterious", "atmospheric"]
        assert result["genre"] == "drama"
    
    def test_fallback_parse_prompts(self):
        """Test fallback prompt parsing"""
        response_text = """
        1. First prompt here
        2. Second prompt there
        # This is a comment
        * Another comment
        """
        result = self.ai_service._fallback_parse_prompts(response_text)
        
        assert len(result) == 2
        assert "First prompt here" in result[0]
        assert "Second prompt there" in result[1]
