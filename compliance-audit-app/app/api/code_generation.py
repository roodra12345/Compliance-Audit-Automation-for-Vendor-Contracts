from flask import request, jsonify, current_app, Blueprint
from openai import OpenAI
import os
from app.utils.audit_logger import log_action

# Create blueprint
code_gen_bp = Blueprint('code_generation', __name__)

@code_gen_bp.route('/generate-code', methods=['POST'])
def generate_code():
    """Generate code using OpenAI GPT-4 without JWT authentication"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('prompt'):
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Get OpenAI API key from request or environment
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        
        if not openai_api_key:
            return jsonify({
                'error': 'OpenAI API key is required. Please provide it in the request or set OPENAI_API_KEY environment variable'
            }), 400
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Prepare the system message for code generation
        system_message = """You are an expert code generator assistant. Generate clean, well-documented, and production-ready code based on the user's requirements. 
        Follow best practices and include error handling where appropriate."""
        
        # Additional parameters from request
        language = data.get('language', 'python')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        
        # Create the prompt with language context
        full_prompt = f"Generate {language} code for the following requirement:\n\n{data['prompt']}"
        
        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract the generated code
        generated_code = response.choices[0].message.content
        
        # Log the action (without sensitive data)
        log_action('anonymous', 'code_generation', 'api', None, {
            'language': language,
            'prompt_length': len(data['prompt'])
        })
        
        return jsonify({
            'success': True,
            'code': generated_code,
            'language': language,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Code generation failed: {str(e)}',
            'success': False
        }), 500


@code_gen_bp.route('/generate-contract-code', methods=['POST'])
def generate_contract_code():
    """Generate code specifically for contract analysis without JWT"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('contract_text'):
            return jsonify({'error': 'Contract text is required'}), 400
        
        if not data.get('task'):
            return jsonify({'error': 'Task description is required'}), 400
        
        # Get OpenAI API key
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        
        if not openai_api_key:
            return jsonify({
                'error': 'OpenAI API key is required'
            }), 400
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Prepare the system message for contract-specific code generation
        system_message = """You are an expert in contract analysis and code generation. 
        Generate Python code that can analyze contracts, extract information, and perform the requested task.
        Use appropriate libraries like pandas, regex, nltk, or spacy as needed.
        Include proper error handling and documentation."""
        
        # Create the prompt
        full_prompt = f"""Given the following contract text, generate Python code to {data['task']}:

Contract Text:
{data['contract_text'][:2000]}  # Limit contract text to avoid token limits

Task: {data['task']}

Generate complete, runnable Python code with:
1. All necessary imports
2. Clear function definitions
3. Error handling
4. Comments explaining the logic
5. Example usage at the bottom
"""
        
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        generated_code = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'code': generated_code,
            'task': data['task'],
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Contract code generation failed: {str(e)}',
            'success': False
        }), 500


@code_gen_bp.route('/analyze-with-ocr', methods=['POST'])
def analyze_with_ocr():
    """Analyze document with OCR and generate code for processing"""
    try:
        data = request.get_json()
        
        # Check for required fields
        if not data.get('image_url') and not data.get('image_base64'):
            return jsonify({'error': 'Either image_url or image_base64 is required'}), 400
        
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key is required'}), 400
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Prepare the message for GPT-4 Vision
        messages = [
            {
                "role": "system",
                "content": """You are an expert at analyzing documents and generating code. 
                First, extract all text from the image using OCR capabilities.
                Then, based on the extracted text and the user's task, generate appropriate Python code."""
            }
        ]
        
        # Add user message with image
        user_content = [
            {
                "type": "text",
                "text": f"Extract text from this image and then generate Python code to: {data.get('task', 'analyze the extracted content')}"
            }
        ]
        
        if data.get('image_url'):
            user_content.append({
                "type": "image_url",
                "image_url": {"url": data['image_url']}
            })
        elif data.get('image_base64'):
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{data['image_base64']}"}
            })
        
        messages.append({"role": "user", "content": user_content})
        
        # Make the API call with GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'result': result,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'OCR analysis failed: {str(e)}',
            'success': False
        }), 500


@code_gen_bp.route('/test-openai-key', methods=['POST'])
def test_openai_key():
    """Test if the provided OpenAI API key is valid"""
    try:
        data = request.get_json()
        openai_api_key = data.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        
        if not openai_api_key:
            return jsonify({
                'valid': False,
                'error': 'No OpenAI API key provided'
            }), 400
        
        # Try to make a simple API call
        client = OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say 'API key is valid'"}],
            max_tokens=10
        )
        
        return jsonify({
            'valid': True,
            'message': 'OpenAI API key is valid and working',
            'models_available': ['gpt-4', 'gpt-4-vision-preview']
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 400