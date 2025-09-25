"""
AI Service for moodboard generation using Google Gemini
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional

class AIService:
    """Service for AI-powered moodboard generation"""
    
    def __init__(self):
        """Initialize the AI service with Gemini API"""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
            response = self.model.generate_content(prompt)
            
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
            
            response = self.model.generate_content(prompt)
            
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
            
            response = self.model.generate_content(prompt)
            
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
