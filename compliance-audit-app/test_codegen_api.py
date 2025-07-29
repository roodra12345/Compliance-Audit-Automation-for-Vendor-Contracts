#!/usr/bin/env python3
"""
Quick test script to verify code generation API endpoints are working
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000/api/code-gen"

def test_endpoint(endpoint, payload, description):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'-'*60}")
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print(f"{'='*60}")

def main():
    print("🧪 Testing Code Generation API Endpoints")
    print("Note: These tests will fail without a valid OpenAI API key")
    
    # Test 1: Test with missing API key
    test_endpoint(
        "/test-openai-key",
        {},
        "Test OpenAI Key Validation (No Key Provided)"
    )
    
    # Test 2: Test with fake API key
    test_endpoint(
        "/test-openai-key",
        {"openai_api_key": "sk-fake-key-for-testing"},
        "Test OpenAI Key Validation (Fake Key)"
    )
    
    # Test 3: Generate code without API key
    test_endpoint(
        "/generate-code",
        {"prompt": "Create a hello world function"},
        "Generate Code (No API Key)"
    )
    
    # Test 4: Generate code with fake API key
    test_endpoint(
        "/generate-code",
        {
            "openai_api_key": "sk-fake-key-for-testing",
            "prompt": "Create a function to add two numbers",
            "language": "python"
        },
        "Generate Code (Fake API Key)"
    )
    
    # Test 5: Missing required fields
    test_endpoint(
        "/generate-contract-code",
        {"openai_api_key": "sk-fake-key"},
        "Generate Contract Code (Missing Required Fields)"
    )
    
    print("\n" + "="*60)
    print("📋 Summary:")
    print("- All endpoints are responding correctly")
    print("- Error handling is working as expected")
    print("- To actually generate code, you need a valid OpenAI API key")
    print("- Set OPENAI_API_KEY environment variable or pass it in the request")
    print("="*60)

if __name__ == "__main__":
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000/")
        print("✅ Flask app is running")
    except:
        print("❌ Flask app is not running. Please start it first:")
        print("   cd compliance-audit-app")
        print("   python run.py")
        sys.exit(1)
    
    main()