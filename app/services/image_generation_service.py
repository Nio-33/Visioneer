"""
Image Generation Service for Visioneer
Supports multiple AI image generation providers
"""

import os
import requests
import base64
import io
from typing import List, Dict, Optional, Any
from PIL import Image
import logging
from app.config import Config
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """Service for generating images using various AI providers"""
    
    def __init__(self):
        """Initialize image generation service"""
        self.openai_api_key = Config.OPENAI_API_KEY
        self.gemini_api_key = Config.GEMINI_API_KEY
        self.gemini_service = GeminiService()
        
    def generate_images(self, prompts: List[str], style: str, 
                       provider: str = 'openai') -> List[Dict[str, Any]]:
        """
        Generate images using specified provider
        
        Args:
            prompts: List of image prompts
            style: Visual style preference
            provider: AI provider ('openai', 'gemini', 'replicate')
            
        Returns:
            List of generated image data
        """
        try:
            if provider == 'openai':
                return self._generate_with_openai(prompts, style)
            elif provider == 'gemini':
                return self._generate_with_gemini(prompts, style)
            elif provider == 'replicate':
                return self._generate_with_replicate(prompts, style)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return []
    
    def _generate_with_openai(self, prompts: List[str], style: str) -> List[Dict[str, Any]]:
        """Generate images using OpenAI DALL-E 3"""
        try:
            import openai
            
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            images = []
            
            for i, prompt in enumerate(prompts):
                try:
                    # Enhance prompt with style
                    enhanced_prompt = f"{prompt}, {style} style, high quality, professional"
                    
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=enhanced_prompt,
                        size="1024x1024",
                        quality="hd",
                        n=1
                    )
                    
                    images.append({
                        'url': response.data[0].url,
                        'prompt': prompt,
                        'enhanced_prompt': enhanced_prompt,
                        'index': i,
                        'provider': 'openai'
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to generate image {i}: {str(e)}")
                    continue
            
            return images
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            return []
    
    def _generate_with_gemini(self, prompts: List[str], style: str) -> List[Dict[str, Any]]:
        """Generate images using Gemini 2.5 Flash"""
        try:
            if not self.gemini_api_key:
                raise ValueError("Gemini API key not configured")
            
            images = []
            
            for i, prompt in enumerate(prompts):
                try:
                    # Use Gemini 2.5 Flash for image generation
                    result = self.gemini_service.generate_image(prompt, style)
                    
                    if result['success']:
                        # Convert PIL image to bytes for storage
                        img_bytes = io.BytesIO()
                        result['image'].save(img_bytes, format='JPEG', quality=90)
                        img_bytes = img_bytes.getvalue()
                        
                        # Encode to base64 for URL
                        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                        
                        images.append({
                            'url': f"data:image/jpeg;base64,{img_base64}",
                            'prompt': prompt,
                            'enhanced_prompt': result['prompt'],
                            'index': i,
                            'provider': 'gemini-2.5-flash',
                            'image_data': img_bytes,
                            'style': style
                        })
                    else:
                        logger.error(f"Gemini generation failed for prompt {i}: {result.get('error', 'Unknown error')}")
                        continue
                    
                except Exception as e:
                    logger.error(f"Failed to generate image {i}: {str(e)}")
                    continue
            
            return images
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            return []
    
    def _generate_with_replicate(self, prompts: List[str], style: str) -> List[Dict[str, Any]]:
        """Generate images using Replicate API"""
        try:
            import replicate
            
            if not os.getenv('REPLICATE_API_TOKEN'):
                raise ValueError("Replicate API token not configured")
            
            images = []
            
            for i, prompt in enumerate(prompts):
                try:
                    enhanced_prompt = f"{prompt}, {style} style, high quality"
                    
                    # Use Stable Diffusion via Replicate
                    output = replicate.run(
                        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                        input={
                            "prompt": enhanced_prompt,
                            "width": 1024,
                            "height": 1024,
                            "num_outputs": 1
                        }
                    )
                    
                    images.append({
                        'url': output[0] if output else None,
                        'prompt': prompt,
                        'enhanced_prompt': enhanced_prompt,
                        'index': i,
                        'provider': 'replicate'
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to generate image {i}: {str(e)}")
                    continue
            
            return images
            
        except Exception as e:
            logger.error(f"Replicate generation failed: {str(e)}")
            return []
    
    def download_and_optimize_image(self, image_url: str, 
                                  max_size: tuple = (1024, 1024)) -> Optional[bytes]:
        """
        Download and optimize image
        
        Args:
            image_url: URL of the image to download
            max_size: Maximum size for optimization
            
        Returns:
            Optimized image bytes or None
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Optimize and save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to download/optimize image: {str(e)}")
            return None
    
    def create_image_grid(self, images: List[Dict[str, Any]], 
                         grid_size: tuple = (2, 2)) -> Optional[bytes]:
        """
        Create a grid of images
        
        Args:
            images: List of image data
            grid_size: Grid dimensions (rows, cols)
            
        Returns:
            Grid image bytes or None
        """
        try:
            if not images:
                return None
            
            # Download and process images
            processed_images = []
            for img_data in images[:grid_size[0] * grid_size[1]]:
                if 'url' in img_data:
                    img_bytes = self.download_and_optimize_image(img_data['url'])
                    if img_bytes:
                        img = Image.open(io.BytesIO(img_bytes))
                        processed_images.append(img)
            
            if not processed_images:
                return None
            
            # Calculate grid dimensions
            img_width, img_height = processed_images[0].size
            grid_width = img_width * grid_size[1]
            grid_height = img_height * grid_size[0]
            
            # Create grid image
            grid_image = Image.new('RGB', (grid_width, grid_height))
            
            for i, img in enumerate(processed_images):
                row = i // grid_size[1]
                col = i % grid_size[1]
                x = col * img_width
                y = row * img_height
                grid_image.paste(img, (x, y))
            
            # Save grid to bytes
            output = io.BytesIO()
            grid_image.save(output, format='JPEG', quality=90)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create image grid: {str(e)}")
            return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available image generation providers"""
        providers = []
        
        if self.openai_api_key:
            providers.append('openai')
        
        if self.gemini_api_key:
            providers.append('gemini')
        
        if os.getenv('REPLICATE_API_TOKEN'):
            providers.append('replicate')
        
        return providers
