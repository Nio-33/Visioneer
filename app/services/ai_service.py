"""
AI Service for moodboard generation using Google Gemini 2.5 Flash Image (Nano Banana)
"""

import os
import base64
import io
from PIL import Image
import google.generativeai as genai
from typing import Dict, List, Optional, Union, Tuple
import logging

class AIService:
    """Service for AI-powered moodboard generation with advanced image capabilities"""
    
    def __init__(self):
        """Initialize the AI service with Gemini 2.5 Flash Image API"""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        # Use Gemini 2.5 Flash Image (Nano Banana) for advanced image generation
        self.text_model = genai.GenerativeModel('gemini-1.5-flash')
        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        self.logger = logging.getLogger(__name__)
    
    def generate_moodboard_concept(self, story: str, style: str, image_count: int, 
                                 aspect_ratio: str) -> Dict:
        """
        Generate a moodboard concept using AI
        
        Args:
            story: The story description
            style: Visual style preference
            image_count: Number of images to generate
            aspect_ratio: Aspect ratio for images
            
        Returns:
            Dictionary containing the generated concept
        """
        try:
            prompt = self._create_moodboard_prompt(story, style, image_count, aspect_ratio)
            response = self.text_model.generate_content(prompt)
            
            return {
                'status': 'success',
                'concept': response.text,
                'raw_response': response.text
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _create_moodboard_prompt(self, story: str, style: str, image_count: int, 
                               aspect_ratio: str) -> str:
        """Create a detailed prompt for moodboard generation"""
        return f"""
        You are a professional visual consultant for filmmakers. Create a detailed moodboard concept for the following project:

        STORY DESCRIPTION:
        {story}

        VISUAL STYLE: {style}
        NUMBER OF IMAGES: {image_count}
        ASPECT RATIO: {aspect_ratio}

        Please provide a comprehensive moodboard concept that includes:

        1. VISUAL ELEMENTS: Describe the key visual elements that should be included in each image
        2. COLOR PALETTE: Suggest a cohesive color scheme with specific hex codes
        3. MOOD & ATMOSPHERE: Describe the overall mood and emotional tone
        4. LIGHTING: Specify lighting conditions and mood
        5. COMPOSITION: Suggest composition styles and framing
        6. TEXTURE & MATERIALS: Describe surface textures and material qualities
        7. STYLE REFERENCES: Suggest visual references and inspirations

        Format your response as a structured analysis that a filmmaker could use to create or commission visual assets. Be specific and detailed in your descriptions.

        Focus on creating a cohesive visual narrative that supports the story's themes and emotional journey.
        """
    
    def refine_moodboard_concept(self, original_concept: str, feedback: str) -> Dict:
        """
        Refine an existing moodboard concept based on feedback
        
        Args:
            original_concept: The original moodboard concept
            feedback: User feedback for refinement
            
        Returns:
            Dictionary containing the refined concept
        """
        try:
            prompt = f"""
            Please refine the following moodboard concept based on the user feedback:

            ORIGINAL CONCEPT:
            {original_concept}

            USER FEEDBACK:
            {feedback}

            Please provide an updated and refined moodboard concept that addresses the feedback while maintaining the core vision.
            """
            
            response = self.text_model.generate_content(prompt)
            
            return {
                'status': 'success',
                'refined_concept': response.text
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_image_prompts(self, moodboard_concept: str, image_count: int) -> List[str]:
        """
        Generate specific image prompts from a moodboard concept
        
        Args:
            moodboard_concept: The moodboard concept description
            image_count: Number of image prompts to generate
            
        Returns:
            List of specific image prompts
        """
        try:
            prompt = f"""
            Based on this moodboard concept, create {image_count} specific image prompts for AI image generation:

            MOODBOARD CONCEPT:
            {moodboard_concept}

            For each image, provide:
            1. A detailed visual description
            2. Specific composition and framing
            3. Lighting and mood details
            4. Color palette notes
            5. Style and aesthetic direction

            Format each prompt as a single, comprehensive description that could be used directly with an AI image generator.
            """
            
            response = self.text_model.generate_content(prompt)
            
            # Parse the response into individual prompts
            prompts = self._parse_image_prompts(response.text, image_count)
            
            return prompts
            
        except Exception as e:
            return [f"Error generating prompts: {str(e)}"]
    
    def _parse_image_prompts(self, response_text: str, expected_count: int) -> List[str]:
        """Parse the AI response into individual image prompts"""
        # Simple parsing - in production, you might want more sophisticated parsing
        lines = response_text.split('\n')
        prompts = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('*'):
                # Clean up the line
                line = line.replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '')
                line = line.replace('Image', '').replace('Prompt', '').strip()
                if line:
                    prompts.append(line)
        
        # Ensure we have the expected number of prompts
        while len(prompts) < expected_count:
            prompts.append(f"Additional moodboard image: {prompts[-1] if prompts else 'Visual element for the story'}")
        
        return prompts[:expected_count]
    
    def generate_image_with_nano_banana(self, prompt: str, style_guidance: str = "") -> Dict:
        """
        Generate a single image using Gemini 2.5 Flash Image (Nano Banana)
        
        Args:
            prompt: Detailed image generation prompt
            style_guidance: Additional style guidance
            
        Returns:
            Dict containing generated image data and metadata
        """
        try:
            enhanced_prompt = f"""
            Create a photorealistic image with the following specifications:
            
            {prompt}
            
            Style Guidance: {style_guidance}
            
            Please ensure the image is:
            - High quality and photorealistic
            - Well-composed with good lighting
            - Professional and visually appealing
            - Suitable for a creative moodboard
            """
            
            response = self.image_model.generate_content(enhanced_prompt)
            
            # Process the response to extract images
            images = []
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Convert bytes to PIL Image
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))
                    images.append(image)
            
            return {
                'images': images,
                'success': True,
                'model_used': 'gemini-2.5-flash-image-preview',
                'prompt_used': enhanced_prompt
            }
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            return {
                'images': [],
                'success': False,
                'error': str(e)
            }
    
    def edit_image_with_nano_banana(self, image: Image.Image, edit_prompt: str) -> Dict:
        """
        Edit an existing image using Gemini 2.5 Flash Image
        
        Args:
            image: PIL Image to edit
            edit_prompt: Description of desired edits
            
        Returns:
            Dict containing edited image data
        """
        try:
            prompt = f"""
            Edit the provided image with the following instructions:
            
            {edit_prompt}
            
            Please maintain the overall composition and quality while making the requested changes.
            Ensure the result is photorealistic and professional.
            """
            
            response = self.image_model.generate_content([prompt, image])
            
            # Process the response to extract edited images
            edited_images = []
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    edited_image = Image.open(io.BytesIO(image_data))
                    edited_images.append(edited_image)
            
            return {
                'edited_images': edited_images,
                'success': True,
                'model_used': 'gemini-2.5-flash-image-preview',
                'edit_prompt': edit_prompt
            }
            
        except Exception as e:
            self.logger.error(f"Error editing image: {str(e)}")
            return {
                'edited_images': [],
                'success': False,
                'error': str(e)
            }
    
    def restore_and_colorize_image(self, image: Image.Image, context: str = "") -> Dict:
        """
        Restore and colorize an old or damaged image using Nano Banana
        
        Args:
            image: PIL Image to restore
            context: Additional context about the image (e.g., "photograph from 1932")
            
        Returns:
            Dict containing restored image data
        """
        try:
            prompt = f"""
            Restore and colorize this image.
            
            {f"Context: {context}" if context else ""}
            
            Please:
            - Fix any damage, scratches, or imperfections
            - Add realistic and historically appropriate colors
            - Maintain the original composition and character
            - Ensure the result looks natural and professional
            """
            
            response = self.image_model.generate_content([prompt, image])
            
            restored_images = []
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    restored_image = Image.open(io.BytesIO(image_data))
                    restored_images.append(restored_image)
            
            return {
                'restored_images': restored_images,
                'success': True,
                'model_used': 'gemini-2.5-flash-image-preview',
                'restoration_context': context
            }
            
        except Exception as e:
            self.logger.error(f"Error restoring image: {str(e)}")
            return {
                'restored_images': [],
                'success': False,
                'error': str(e)
            }
    
    def create_conversational_edit_session(self) -> Dict:
        """
        Create a new conversational editing session for iterative image editing
        
        Returns:
            Dict containing session information
        """
        try:
            # Create a chat session for conversational editing
            chat = self.image_model.start_chat()
            
            return {
                'session_id': id(chat),  # Simple session ID
                'chat_session': chat,
                'success': True,
                'model_used': 'gemini-2.5-flash-image-preview'
            }
            
        except Exception as e:
            self.logger.error(f"Error creating chat session: {str(e)}")
            return {
                'session_id': None,
                'chat_session': None,
                'success': False,
                'error': str(e)
            }
    
    def send_conversational_edit(self, chat_session, message: str, image: Image.Image = None) -> Dict:
        """
        Send a message to the conversational editing session
        
        Args:
            chat_session: Active chat session
            message: Text message for the edit
            image: Optional image to include
            
        Returns:
            Dict containing the response and any generated images
        """
        try:
            if image:
                response = chat_session.send_message([message, image])
            else:
                response = chat_session.send_message(message)
            
            # Process response for images
            generated_images = []
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    generated_image = Image.open(io.BytesIO(image_data))
                    generated_images.append(generated_image)
            
            return {
                'response_text': response.text if hasattr(response, 'text') else "",
                'generated_images': generated_images,
                'success': True,
                'model_used': 'gemini-2.5-flash-image-preview'
            }
            
        except Exception as e:
            self.logger.error(f"Error in conversational edit: {str(e)}")
            return {
                'response_text': "",
                'generated_images': [],
                'success': False,
                'error': str(e)
            }
