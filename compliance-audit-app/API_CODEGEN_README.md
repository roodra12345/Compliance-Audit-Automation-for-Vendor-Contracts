# Code Generation API Documentation (No JWT Required)

This API provides code generation capabilities using OpenAI GPT-4, without requiring JWT authentication. You can use your own OpenAI API key directly.

## Base URL
```
http://localhost:5000/api/code-gen
```

## Authentication
No JWT authentication required. Instead, provide your OpenAI API key in the request body:
```json
{
  "openai_api_key": "your-openai-api-key-here"
}
```

Alternatively, set the `OPENAI_API_KEY` environment variable.

## Endpoints

### 1. Test OpenAI Key
**Endpoint:** `POST /test-openai-key`

Test if your OpenAI API key is valid.

**Request Body:**
```json
{
  "openai_api_key": "sk-..."
}
```

**Response:**
```json
{
  "valid": true,
  "message": "OpenAI API key is valid and working",
  "models_available": ["gpt-4", "gpt-4-vision-preview"]
}
```

### 2. Generate Code
**Endpoint:** `POST /generate-code`

Generate code based on a natural language prompt.

**Request Body:**
```json
{
  "openai_api_key": "sk-...",
  "prompt": "Create a function to validate email addresses",
  "language": "python",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Parameters:**
- `prompt` (required): Description of what code to generate
- `language` (optional): Programming language (default: "python")
- `temperature` (optional): Creativity level 0-1 (default: 0.7)
- `max_tokens` (optional): Maximum response length (default: 2000)

**Response:**
```json
{
  "success": true,
  "code": "import re\n\ndef validate_email(email):\n    ...",
  "language": "python",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

### 3. Generate Contract Analysis Code
**Endpoint:** `POST /generate-contract-code`

Generate code specifically for analyzing contracts.

**Request Body:**
```json
{
  "openai_api_key": "sk-...",
  "contract_text": "This Service Agreement...",
  "task": "extract payment terms and identify compliance requirements"
}
```

**Parameters:**
- `contract_text` (required): The contract text to analyze
- `task` (required): What analysis task to perform

**Response:**
```json
{
  "success": true,
  "code": "import re\nimport pandas as pd\n\ndef analyze_contract(text):\n    ...",
  "task": "extract payment terms and identify compliance requirements",
  "usage": {
    "prompt_tokens": 500,
    "completion_tokens": 800,
    "total_tokens": 1300
  }
}
```

### 4. Analyze Document with OCR
**Endpoint:** `POST /analyze-with-ocr`

Extract text from an image using OCR and generate code for processing it.

**Request Body (with image URL):**
```json
{
  "openai_api_key": "sk-...",
  "image_url": "https://example.com/contract.jpg",
  "task": "extract all contract clauses"
}
```

**Request Body (with base64 image):**
```json
{
  "openai_api_key": "sk-...",
  "image_base64": "iVBORw0KGgoAAAANS...",
  "task": "identify compliance requirements"
}
```

**Parameters:**
- `image_url` or `image_base64` (one required): The document image
- `task` (optional): What to do with the extracted text

**Response:**
```json
{
  "success": true,
  "result": "Extracted text:\n[Document content]\n\nGenerated code:\n...",
  "usage": {
    "prompt_tokens": 1000,
    "completion_tokens": 1500,
    "total_tokens": 2500
  }
}
```

## Example Usage

### Python Example
```python
import requests

# Test your API key
response = requests.post(
    "http://localhost:5000/api/code-gen/test-openai-key",
    json={"openai_api_key": "sk-..."}
)
print(response.json())

# Generate code
response = requests.post(
    "http://localhost:5000/api/code-gen/generate-code",
    json={
        "openai_api_key": "sk-...",
        "prompt": "Create a REST API client in Python",
        "language": "python"
    }
)
result = response.json()
print(result['code'])
```

### cURL Example
```bash
# Test API key
curl -X POST http://localhost:5000/api/code-gen/test-openai-key \
  -H "Content-Type: application/json" \
  -d '{"openai_api_key": "sk-..."}'

# Generate code
curl -X POST http://localhost:5000/api/code-gen/generate-code \
  -H "Content-Type: application/json" \
  -d '{
    "openai_api_key": "sk-...",
    "prompt": "Create a function to sort an array",
    "language": "javascript"
  }'
```

### JavaScript Example
```javascript
// Generate contract analysis code
fetch('http://localhost:5000/api/code-gen/generate-contract-code', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    openai_api_key: 'sk-...',
    contract_text: 'Contract text here...',
    task: 'extract key dates and deadlines'
  })
})
.then(response => response.json())
.then(data => console.log(data.code));
```

## Error Handling

All endpoints return errors in this format:
```json
{
  "error": "Error message",
  "success": false
}
```

Common errors:
- Missing OpenAI API key
- Invalid API key
- Missing required parameters
- Token limit exceeded
- Rate limiting

## Best Practices

1. **API Key Security**: Never expose your OpenAI API key in client-side code
2. **Token Usage**: Monitor token usage to control costs
3. **Error Handling**: Always check the `success` field in responses
4. **Rate Limiting**: Implement appropriate delays between requests
5. **Contract Text**: Limit contract text to 2000 characters to avoid token limits

## Running the Example Script

```bash
cd compliance-audit-app/examples
# Edit code_generation_example.py and add your OpenAI API key
python code_generation_example.py
```

## Cost Estimation

GPT-4 pricing (as of 2024):
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

Example costs:
- Simple code generation: ~$0.02-0.05
- Contract analysis: ~$0.05-0.15
- OCR + analysis: ~$0.10-0.30

## Support

For issues or questions:
1. Check your OpenAI API key is valid
2. Ensure you have sufficient OpenAI credits
3. Check the error messages in responses
4. Review the example script for usage patterns