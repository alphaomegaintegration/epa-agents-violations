#!/usr/bin/env python3
"""
Debug Anthropic API Integration
Test if the API key works and identify issues
"""

import os
import asyncio
import aiohttp
import json

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not available")

async def test_anthropic_api():
    """Test basic Anthropic API call"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"🔑 API Key Found: {'Yes' if api_key else 'No'}")
    
    if api_key:
        print(f"🔑 API Key Preview: {api_key[:20]}...{api_key[-10:]}")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Test API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Test: What is 2+2? Respond with just the number."}
        ]
    }
    
    print("🧪 Testing Anthropic API...")
    print(f"📡 URL: {url}")
    print(f"🤖 Model: {payload['model']}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"📈 Status Code: {response.status}")
                print(f"📋 Headers: {dict(response.headers)}")
                
                response_text = await response.text()
                print(f"📄 Raw Response Length: {len(response_text)} chars")
                print(f"📄 Raw Response Preview: {response_text[:500]}...")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("✅ API Call Successful!")
                        print(f"🎯 Response: {result}")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Parse Error: {e}")
                        return False
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"❌ Error Response: {response_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Request Exception: {e}")
        print(f"❌ Exception Type: {type(e)}")
        return False

async def main():
    print("🔍 ANTHROPIC API DEBUG TEST")
    print("=" * 50)
    
    success = await test_anthropic_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ RESULT: API Working - Issue is in agent implementation")
    else:
        print("❌ RESULT: API Not Working - Fix API configuration")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())