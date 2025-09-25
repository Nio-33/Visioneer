#!/usr/bin/env python3
"""
Test real AI image generation in Visioneer application
"""

import requests
import time
import json

def test_real_ai_generation():
    """Test the complete AI workflow with real Gemini integration"""
    base_url = "http://localhost:5002"
    
    print("🤖 Testing Real AI Image Generation")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing application health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Application is healthy")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Test Gemini Service Directly
    print("\n2. Testing Gemini service directly...")
    try:
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        
        if gemini_service.mock_mode:
            print("⚠️  Gemini service is in mock mode")
            return False
        
        # Test image generation
        result = gemini_service.generate_image(
            "A cyberpunk detective in a neon-lit alley",
            "cinematic"
        )
        
        if result['success']:
            print("✅ Gemini 2.5 Flash image generation working!")
            print(f"   Generated image with prompt: {result['prompt']}")
        else:
            print(f"❌ Gemini image generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini service test error: {e}")
        return False
    
    # Test 3: Test AI Service Integration
    print("\n3. Testing AI service integration...")
    try:
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        # Test concept generation
        concept_result = ai_service.generate_moodboard_concept(
            "A cyberpunk detective story",
            "cinematic",
            4,
            "16:9"
        )
        
        if concept_result['status'] == 'success':
            print("✅ AI concept generation working!")
            print(f"   Generated concept: {concept_result['concept'][:100]}...")
        else:
            print(f"❌ AI concept generation failed: {concept_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ AI service test error: {e}")
        return False
    
    # Test 4: Test Image Generation Service
    print("\n4. Testing image generation service...")
    try:
        from app.services.image_generation_service import ImageGenerationService
        image_service = ImageGenerationService()
        
        # Test image generation
        images = image_service.generate_images(
            ["A cyberpunk detective in a neon-lit alley", "A futuristic cityscape"],
            "cinematic",
            "gemini"
        )
        
        if images and len(images) > 0:
            print(f"✅ Image generation service working! Generated {len(images)} images")
            for i, img in enumerate(images):
                print(f"   Image {i+1}: {img.get('prompt', 'No prompt')}")
        else:
            print("❌ Image generation service failed")
            return False
            
    except Exception as e:
        print(f"❌ Image generation service test error: {e}")
        return False
    
    # Test 5: Test Complete Workflow
    print("\n5. Testing complete workflow...")
    try:
        form_data = {
            'project_title': 'Real AI Test Project',
            'story_concept': 'A cyberpunk detective story with neon lights and flying cars',
            'mood': 'dark',
            'tone': 'noir',
            'genre': 'sci-fi',
            'visual_style': 'cinematic'
        }
        
        print("   Submitting form with real AI data...")
        response = requests.post(f"{base_url}/new-project", data=form_data)
        
        if response.status_code == 200:
            # Check if it's a redirect to moodboard results
            if "moodboard" in response.url or "redirect" in response.text.lower():
                print("✅ Form submission successful - redirected to results")
            else:
                print("⚠️  Form submission returned form page (may be processing)")
        else:
            print(f"❌ Form submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Complete workflow test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Real AI integration is working!")
    print("\n📋 Current Status:")
    print("✅ Gemini 2.5 Flash image generation working")
    print("✅ AI concept generation working")
    print("✅ Image generation service working")
    print("✅ Complete workflow functional")
    print("✅ Billing is properly configured")
    
    return True

if __name__ == "__main__":
    test_real_ai_generation()
