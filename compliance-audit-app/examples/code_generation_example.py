"""
Example script demonstrating how to use the code generation API endpoints
without JWT authentication, using OpenAI GPT-4 keys directly.
"""

import requests
import json
import base64
from typing import Optional

# Base URL for the API (adjust as needed)
BASE_URL = "http://localhost:5000/api/code-gen"

# Your OpenAI API key
OPENAI_API_KEY = "your-openai-api-key-here"  # Replace with your actual key


def test_api_key():
    """Test if the OpenAI API key is valid"""
    url = f"{BASE_URL}/test-openai-key"
    payload = {
        "openai_api_key": OPENAI_API_KEY
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get('valid'):
        print("✅ API Key is valid!")
        print(f"Available models: {result.get('models_available')}")
    else:
        print(f"❌ API Key is invalid: {result.get('error')}")
    
    return result.get('valid', False)


def generate_code(prompt: str, language: str = "python"):
    """Generate code based on a prompt"""
    url = f"{BASE_URL}/generate-code"
    payload = {
        "openai_api_key": OPENAI_API_KEY,
        "prompt": prompt,
        "language": language,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    print(f"\n📝 Generating {language} code for: {prompt[:50]}...")
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get('success'):
        print("\n✅ Code generated successfully!")
        print(f"Token usage: {result.get('usage')}")
        print("\n--- Generated Code ---")
        print(result.get('code'))
        print("--- End of Code ---\n")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result


def generate_contract_code(contract_text: str, task: str):
    """Generate code specifically for contract analysis"""
    url = f"{BASE_URL}/generate-contract-code"
    payload = {
        "openai_api_key": OPENAI_API_KEY,
        "contract_text": contract_text,
        "task": task
    }
    
    print(f"\n📄 Generating contract analysis code for task: {task}")
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get('success'):
        print("\n✅ Contract analysis code generated!")
        print(f"Token usage: {result.get('usage')}")
        print("\n--- Generated Code ---")
        print(result.get('code'))
        print("--- End of Code ---\n")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result


def analyze_document_with_ocr(image_path: Optional[str] = None, 
                             image_url: Optional[str] = None, 
                             task: str = "extract and analyze text"):
    """Analyze a document image using OCR and generate code"""
    url = f"{BASE_URL}/analyze-with-ocr"
    payload = {
        "openai_api_key": OPENAI_API_KEY,
        "task": task
    }
    
    # Add image data
    if image_path:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            payload["image_base64"] = encoded_image
    elif image_url:
        payload["image_url"] = image_url
    else:
        print("❌ Error: Either image_path or image_url must be provided")
        return None
    
    print(f"\n🖼️ Analyzing document with OCR for task: {task}")
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get('success'):
        print("\n✅ Document analyzed successfully!")
        print(f"Token usage: {result.get('usage')}")
        print("\n--- Analysis Result ---")
        print(result.get('result'))
        print("--- End of Result ---\n")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result


def main():
    """Run example demonstrations"""
    print("🚀 Code Generation API Examples (No JWT Required)")
    print("=" * 50)
    
    # Test API key first
    if not test_api_key():
        print("\n⚠️  Please update OPENAI_API_KEY with a valid key before continuing.")
        return
    
    # Example 1: General code generation
    print("\n\n📌 Example 1: General Code Generation")
    generate_code(
        prompt="Create a function to validate email addresses using regex",
        language="python"
    )
    
    # Example 2: Contract-specific code generation
    print("\n\n📌 Example 2: Contract Analysis Code Generation")
    sample_contract = """
    This Service Agreement is entered into on January 1, 2024, between 
    ABC Corporation (Service Provider) and XYZ Company (Client).
    
    Services: The Service Provider agrees to provide IT consulting services.
    Payment: $10,000 per month, payable within 30 days.
    Term: 12 months with automatic renewal.
    Penalties: Late payment incurs 2% monthly interest.
    Compliance: Must comply with ISO 27001 standards.
    """
    
    generate_contract_code(
        contract_text=sample_contract,
        task="extract payment terms and compliance requirements"
    )
    
    # Example 3: Generate code for multiple languages
    print("\n\n📌 Example 3: Multi-language Code Generation")
    languages = ["javascript", "java", "go"]
    prompt = "Create a function to calculate fibonacci numbers"
    
    for lang in languages:
        generate_code(prompt=prompt, language=lang)
    
    # Example 4: OCR analysis (if you have an image)
    print("\n\n📌 Example 4: OCR Document Analysis")
    print("Note: Uncomment and provide an image path or URL to test OCR functionality")
    
    # Uncomment to test with a local image:
    # analyze_document_with_ocr(
    #     image_path="path/to/contract/image.jpg",
    #     task="extract all contract clauses and create a summary"
    # )
    
    # Or test with an image URL:
    # analyze_document_with_ocr(
    #     image_url="https://example.com/contract-image.jpg",
    #     task="identify compliance requirements mentioned in the document"
    # )


if __name__ == "__main__":
    main()