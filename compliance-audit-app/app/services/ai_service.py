import json
from typing import List, Dict, Optional
from openai import AzureOpenAI, OpenAI
import re
from datetime import datetime, date
import os

class AIService:
    def __init__(self, endpoint: str = None, key: str = None, deployment_name: str = None):
        self.endpoint = endpoint
        self.key = key
        self.deployment_name = deployment_name or 'gpt-4'
        self.client = None
        
        # Try OpenAI API first (simpler setup)
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.client = OpenAI(api_key=openai_key)
            self.is_azure = False
        # Fall back to Azure OpenAI if configured
        elif endpoint and key:
            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=key,
                api_version="2024-02-01"
            )
            self.is_azure = True
    
    def analyze_contract(self, contract_text: str) -> Dict[str, any]:
        """Analyze contract text and extract key information"""
        if not self.client:
            return {'error': 'AI service not configured'}
        
        try:
            # Extract contract metadata
            metadata = self._extract_contract_metadata(contract_text)
            
            # Detect and analyze clauses
            clauses = self._detect_clauses(contract_text)
            
            # Assess overall risk
            risk_assessment = self._assess_contract_risk(clauses)
            
            return {
                'metadata': metadata,
                'clauses': clauses,
                'risk_assessment': risk_assessment,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _extract_contract_metadata(self, text: str) -> Dict:
        """Extract basic contract information"""
        prompt = """
        Extract the following information from the contract text:
        1. Contract parties (vendor/supplier name and buyer/customer name)
        2. Contract start date
        3. Contract end date
        4. Contract value/amount if mentioned
        5. Payment terms
        6. Contract title or description
        
        Return as JSON with keys: vendor_name, customer_name, start_date, end_date, contract_value, currency, payment_terms, title
        Use null for missing values. Dates should be in YYYY-MM-DD format.
        
        Contract text:
        {text}
        """
        
        try:
            # Use appropriate model name based on API type
            model_name = self.deployment_name if self.is_azure else "gpt-4"
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a contract analysis expert. Extract information accurately and return valid JSON."},
                    {"role": "user", "content": prompt.format(text=text[:4000])}  # Limit text length
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
            
        except Exception as e:
            print(f"Metadata extraction error: {e}")
            return {}
    
    def _detect_clauses(self, text: str) -> List[Dict]:
        """Detect and categorize important clauses"""
        prompt = """
        Analyze the contract and identify important clauses. For each clause found, provide:
        1. clause_type: One of ['regulatory', 'financial', 'penalty', 'renewal', 'termination', 'liability', 'warranty', 'confidentiality', 'other']
        2. clause_subtype: For regulatory, specify the standard (ISO, FDA, GDP, GMP, etc.)
        3. title: Brief title for the clause
        4. content: The actual clause text (limit to 500 characters)
        5. summary: Brief summary of what the clause means
        6. compliance_requirement: What needs to be done to comply (if applicable)
        7. risk_assessment: 'low', 'medium', or 'high'
        8. action_required: true/false
        9. financial_amount: If clause involves money
        10. penalty_trigger: What triggers the penalty (for penalty clauses)
        
        Focus on:
        - Regulatory compliance requirements (ISO, FDA, GDP, GMP, etc.)
        - Financial obligations and payment terms
        - Penalties for non-compliance
        - Renewal and termination conditions
        - Liability and warranty terms
        
        Return as JSON array. Maximum 20 most important clauses.
        
        Contract text:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a legal contract analyst specializing in compliance. Identify and analyze contract clauses accurately."},
                    {"role": "user", "content": prompt.format(text=text[:6000])}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            result = response.choices[0].message.content
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                clauses = json.loads(json_match.group())
                # Ensure all clauses have required fields
                for clause in clauses:
                    clause.setdefault('clause_type', 'other')
                    clause.setdefault('risk_assessment', 'medium')
                    clause.setdefault('action_required', False)
                return clauses
            return []
            
        except Exception as e:
            print(f"Clause detection error: {e}")
            return []
    
    def _assess_contract_risk(self, clauses: List[Dict]) -> Dict:
        """Assess overall contract risk based on detected clauses"""
        if not clauses:
            return {
                'overall_risk': 'medium',
                'risk_factors': [],
                'recommendations': []
            }
        
        high_risk_count = sum(1 for c in clauses if c.get('risk_assessment') == 'high')
        medium_risk_count = sum(1 for c in clauses if c.get('risk_assessment') == 'medium')
        
        # Determine overall risk
        if high_risk_count >= 3:
            overall_risk = 'high'
        elif high_risk_count >= 1 or medium_risk_count >= 5:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        # Identify risk factors
        risk_factors = []
        if any(c.get('clause_type') == 'penalty' for c in clauses):
            risk_factors.append('Contains penalty clauses')
        if any(c.get('clause_type') == 'regulatory' for c in clauses):
            risk_factors.append('Subject to regulatory compliance')
        if any(c.get('action_required') for c in clauses):
            risk_factors.append('Immediate action required for some clauses')
        
        # Generate recommendations
        recommendations = []
        if overall_risk in ['high', 'medium']:
            recommendations.append('Schedule detailed compliance review')
        if any(c.get('clause_type') == 'regulatory' for c in clauses):
            recommendations.append('Ensure all regulatory requirements are met')
        if any(c.get('clause_type') == 'renewal' for c in clauses):
            recommendations.append('Set up renewal reminders')
        
        return {
            'overall_risk': overall_risk,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'high_risk_clauses': high_risk_count,
            'medium_risk_clauses': medium_risk_count
        }
    
    def answer_contract_question(self, contract_text: str, question: str) -> str:
        """Answer natural language questions about a contract"""
        if not self.client:
            return "AI service not configured"
        
        prompt = """
        Based on the contract text below, answer the following question accurately and concisely.
        If the information is not in the contract, say so clearly.
        
        Question: {question}
        
        Contract text:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a contract analysis assistant. Answer questions based solely on the contract text provided."},
                    {"role": "user", "content": prompt.format(question=question, text=contract_text[:4000])}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def summarize_contract(self, contract_text: str) -> str:
        """Generate a brief summary of the contract"""
        if not self.client:
            return "AI service not configured"
        
        prompt = """
        Provide a brief executive summary of this contract (maximum 200 words) covering:
        1. Main parties involved
        2. Purpose of the contract
        3. Key obligations
        4. Important dates
        5. Major risks or concerns
        
        Contract text:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a contract analyst. Provide clear, concise summaries."},
                    {"role": "user", "content": prompt.format(text=contract_text[:4000])}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"