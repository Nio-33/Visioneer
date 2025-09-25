#!/usr/bin/env python3
"""
Test script to verify Gemini 2.5 Flash integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple text generation first
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🧪 Testing Gemini text generation...")
        response = model.generate_content("Hello, can you generate a short creative story about a cyberpunk city?")
        
        if response.text:
            print("✅ Gemini text generation working!")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print("❌ No response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini: {str(e)}")
        return False

def test_gemini_image_generation():
    """Test Gemini 2.5 Flash image generation"""
    try:
        from app.services.gemini_service import GeminiService
        
        print("🧪 Testing Gemini 2.5 Flash image generation...")
        
        # Initialize service
        gemini_service = GeminiService()
        
        if gemini_service.mock_mode:
            print("⚠️  Running in mock mode (no API key or API key invalid)")
            return False
        
        # Test image generation
        result = gemini_service.generate_image(
            "A futuristic cyberpunk city with neon lights and flying cars",
            "cinematic"
        )
        
        if result['success']:
            print("✅ Gemini 2.5 Flash image generation working!")
            print(f"Generated image with prompt: {result['prompt']}")
            return True
        else:
            print(f"❌ Image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image generation: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Gemini Integration for Visioneer")
    print("=" * 50)
    
    # Test 1: Basic API connection
    print("\n1. Testing basic Gemini API connection...")
    text_success = test_gemini_api()
    
    # Test 2: Image generation
    print("\n2. Testing Gemini 2.5 Flash image generation...")
    image_success = test_gemini_image_generation()
    
    print("\n" + "=" * 50)
    if text_success and image_success:
        print("🎉 All tests passed! Gemini integration is working!")
    elif text_success:
        print("⚠️  Text generation works, but image generation needs attention")
    else:
        print("❌ Gemini integration needs to be fixed")
    
    print("\nNext steps:")
    print("- If image generation failed, check if Gemini 2.5 Flash is available in your region")
    print("- Make sure billing is set up for Gemini API")
    print("- Verify the API key has the correct permissions")
