"""
Gemini 2.5 Flash Image Generation Service
"""

import os
import logging
from typing import List, Dict, Optional, Union
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for generating images using Gemini 2.5 Flash"""
    
    def __init__(self):
        """Initialize Gemini service"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
    
    def generate_image(self, prompt: str, style: str = "cinematic") -> Dict:
        """
        Generate a single image using Gemini 2.5 Flash
        
        Args:
            prompt: Text description for image generation
            style: Visual style (cinematic, artistic, realistic, etc.)
            
        Returns:
            Dict with image data and metadata
        """
        if self.mock_mode:
            return self._generate_mock_image(prompt, style)
        
        try:
            # Enhance prompt with style information
            enhanced_prompt = f"Create a {style} image: {prompt}. Make it high quality and detailed."
            
            # Generate content
            response = self.model.generate_content(
                enhanced_prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            
            # Process response
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Convert to PIL Image
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        
                        return {
                            'success': True,
                            'image': image,
                            'prompt': enhanced_prompt,
                            'style': style,
                            'model': 'gemini-2.0-flash-exp'
                        }
            
            return {
                'success': False,
                'error': 'No image data received from Gemini',
                'prompt': enhanced_prompt
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini image generation failed: {error_msg}")
            
            # Handle quota exceeded error
            if "quota" in error_msg.lower() or "429" in error_msg:
                return {
                    'success': False,
                    'error': 'Gemini API quota exceeded. Please set up billing to use image generation.',
                    'prompt': prompt,
                    'quota_exceeded': True
                }
            
            return {
                'success': False,
                'error': error_msg,
                'prompt': prompt
            }
    
    def generate_multiple_images(self, prompts: List[str], style: str = "cinematic") -> List[Dict]:
        """
        Generate multiple images using Gemini 2.5 Flash
        
        Args:
            prompts: List of text descriptions for image generation
            style: Visual style for all images
            
        Returns:
            List of image generation results
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f"Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
            result = self.generate_image(prompt, style)
            results.append(result)
        
        return results
    
    def edit_image(self, image: Union[str, Image.Image], edit_prompt: str) -> Dict:
        """
        Edit an existing image using Gemini 2.5 Flash
        
        Args:
            image: Path to image file or PIL Image object
            edit_prompt: Description of desired edits
            
        Returns:
            Dict with edited image data
        """
        if self.mock_mode:
            return self._generate_mock_image(edit_prompt, "edited")
        
        try:
            # Load image if path provided
            if isinstance(image, str):
                image = Image.open(image)
            
            # Create enhanced prompt
            enhanced_prompt = f"Edit this image: {edit_prompt}. Maintain the original style and quality."
            
            # Generate content with image
            response = self.model.generate_content([image, enhanced_prompt])
            
            # Process response
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        edited_image = Image.open(BytesIO(image_data))
                        
                        return {
                            'success': True,
                            'image': edited_image,
                            'prompt': enhanced_prompt,
                            'original_prompt': edit_prompt
                        }
            
            return {
                'success': False,
                'error': 'No edited image data received from Gemini',
                'prompt': enhanced_prompt
            }
            
        except Exception as e:
            logger.error(f"Gemini image editing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prompt': edit_prompt
            }
    
    def create_conversational_session(self) -> 'GeminiChatSession':
        """
        Create a conversational chat session for iterative image editing
        
        Returns:
            GeminiChatSession object
        """
        if self.mock_mode:
            return MockGeminiChatSession()
        
        return GeminiChatSession(self.model)
    
    def _generate_mock_image(self, prompt: str, style: str) -> Dict:
        """Generate mock image for development/testing"""
        import random
        
        # Create a simple colored image as mock
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
        ]
        
        color = random.choice(colors)
        mock_image = Image.new('RGB', (400, 300), color)
        
        return {
            'success': True,
            'image': mock_image,
            'prompt': prompt,
            'style': style,
            'model': 'mock-gemini-2.0-flash-exp'
        }


class GeminiChatSession:
    """Chat session for conversational image editing"""
    
    def __init__(self, model):
        self.model = model
        self.chat = model.start_chat(history=[])
        self.current_image = None
    
    def send_message(self, message: str, image: Optional[Image.Image] = None) -> Dict:
        """
        Send a message to the chat session
        
        Args:
            message: Text message
            image: Optional image to include
            
        Returns:
            Dict with response data
        """
        try:
            if image:
                self.current_image = image
                response = self.chat.send_message([image, message])
            else:
                response = self.chat.send_message(message)
            
            # Process response for images
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        new_image = Image.open(BytesIO(image_data))
                        
                        return {
                            'success': True,
                            'image': new_image,
                            'text': response.text,
                            'message': message
                        }
            
            return {
                'success': True,
                'text': response.text,
                'message': message,
                'image': None
            }
            
        except Exception as e:
            logger.error(f"Chat session error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': message
            }


class MockGeminiChatSession:
    """Mock chat session for development"""
    
    def __init__(self):
        self.current_image = None
    
    def send_message(self, message: str, image: Optional[Image.Image] = None) -> Dict:
        """Mock chat session response"""
        if image:
            self.current_image = image
        
        return {
            'success': True,
            'text': f"Mock response to: {message}",
            'message': message,
            'image': self.current_image
        }
