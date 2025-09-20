"""
AI service integration for Gemini API
"""

import google.generativeai as genai
from flask import current_app
import json
import time
from typing import List, Dict, Optional

class AIService:
    """AI service for story analysis and moodboard generation"""
    
    def __init__(self):
        self.model = None
        self.initialized = False
    
    def initialize(self, api_key: str):
        """Initialize Gemini AI service"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True
            current_app.logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            raise
    
    def analyze_story(self, story_text: str, style: str = "cinematic") -> Dict:
        """
        Analyze story text and extract visual elements
        
        Args:
            story_text: The story description
            style: Visual style preference
            
        Returns:
            Dictionary containing extracted visual elements
        """
        if not self.initialized:
            raise Exception("AI service not initialized")
        
        try:
            prompt = self._create_story_analysis_prompt(story_text, style)
            
            response = self.model.generate_content(prompt)
            
            # Parse the response to extract visual elements
            analysis = self._parse_story_analysis(response.text)
            
            return {
                'success': True,
                'analysis': analysis,
                'raw_response': response.text
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing story: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }
    
    def generate_image_prompts(self, analysis: Dict, image_count: int = 8) -> List[str]:
        """
        Generate specific image prompts based on story analysis
        
        Args:
            analysis: Story analysis results
            image_count: Number of images to generate
            
        Returns:
            List of image generation prompts
        """
        if not self.initialized:
            raise Exception("AI service not initialized")
        
        try:
            prompt = self._create_image_prompt_generation_prompt(analysis, image_count)
            
            response = self.model.generate_content(prompt)
            
            # Parse response to extract image prompts
            image_prompts = self._parse_image_prompts(response.text)
            
            return image_prompts
            
        except Exception as e:
            current_app.logger.error(f"Error generating image prompts: {str(e)}")
            return []
    
    def _create_story_analysis_prompt(self, story_text: str, style: str) -> str:
        """Create prompt for story analysis"""
        return f"""
        Analyze this story description for visual moodboard creation:
        
        Story: "{story_text}"
        
        Style: {style}
        
        Extract the following visual elements and return as JSON:
        1. Setting/Location (primary and secondary locations)
        2. Time Period/Era
        3. Mood/Atmosphere (3-5 descriptive words)
        4. Color Palette (dominant colors and tones)
        5. Lighting (type and quality)
        6. Characters (if any, their visual characteristics)
        7. Key Visual Elements (objects, symbols, themes)
        8. Genre/Style Indicators
        
        Format your response as valid JSON with these exact keys:
        {{
            "setting": ["location1", "location2"],
            "time_period": "era/period",
            "mood": ["mood1", "mood2", "mood3"],
            "colors": ["color1", "color2", "color3"],
            "lighting": "lighting description",
            "characters": ["character description 1", "character description 2"],
            "visual_elements": ["element1", "element2", "element3"],
            "genre": "genre/style"
        }}
        """
    
    def _create_image_prompt_generation_prompt(self, analysis: Dict, image_count: int) -> str:
        """Create prompt for generating image generation prompts"""
        return f"""
        Based on this visual analysis, create {image_count} specific image generation prompts for a cohesive moodboard:
        
        Analysis: {json.dumps(analysis, indent=2)}
        
        Create {image_count} diverse but thematically consistent prompts that cover:
        - Different aspects of the setting
        - Various mood expressions
        - Different compositions and angles
        - Key visual elements and symbols
        - Character moments (if applicable)
        
        Each prompt should be detailed and specific for AI image generation.
        Return as a JSON array of strings:
        ["prompt1", "prompt2", "prompt3", ...]
        """
    
    def _parse_story_analysis(self, response_text: str) -> Dict:
        """Parse story analysis response"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_parse_analysis(response_text)
                
        except json.JSONDecodeError:
            current_app.logger.warning("Failed to parse JSON response, using fallback")
            return self._fallback_parse_analysis(response_text)
    
    def _parse_image_prompts(self, response_text: str) -> List[str]:
        """Parse image prompts from response"""
        try:
            # Try to extract JSON array from response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: split by lines and clean
                lines = response_text.split('\n')
                prompts = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('*'):
                        # Remove numbering and clean
                        prompt = line.lstrip('0123456789.- ')
                        if len(prompt) > 20:  # Reasonable prompt length
                            prompts.append(prompt)
                return prompts[:8]  # Limit to 8 prompts
                
        except json.JSONDecodeError:
            current_app.logger.warning("Failed to parse image prompts JSON, using fallback")
            return self._fallback_parse_prompts(response_text)
    
    def _fallback_parse_analysis(self, response_text: str) -> Dict:
        """Fallback parsing for story analysis"""
        return {
            "setting": ["Unknown location"],
            "time_period": "Contemporary",
            "mood": ["mysterious", "atmospheric"],
            "colors": ["dark", "muted", "dramatic"],
            "lighting": "dramatic lighting",
            "characters": [],
            "visual_elements": ["cinematic composition"],
            "genre": "drama"
        }
    
    def _fallback_parse_prompts(self, response_text: str) -> List[str]:
        """Fallback parsing for image prompts"""
        return [
            "Cinematic wide shot establishing the setting",
            "Close-up detail shot showing mood and atmosphere",
            "Medium shot with dramatic lighting",
            "Atmospheric environmental shot",
            "Character moment with emotional depth",
            "Symbolic visual element representing themes",
            "Textural detail shot adding visual interest",
            "Final composition tying everything together"
        ]

# Global AI service instance
ai_service = AIService()

def initialize_ai_service(api_key: str):
    """Initialize AI service with API key"""
    ai_service.initialize(api_key)
    return ai_service
