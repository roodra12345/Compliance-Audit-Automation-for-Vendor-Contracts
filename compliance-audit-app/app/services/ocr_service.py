import os
import io
import time
from typing import List, Dict, Optional
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import tempfile

class OCRService:
    def __init__(self, endpoint: str, key: str):
        self.endpoint = endpoint
        self.key = key
        self.client = None
        if endpoint and key:
            self.client = ComputerVisionClient(
                endpoint=self.endpoint,
                credentials=CognitiveServicesCredentials(self.key)
            )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF using multiple methods:
        1. Try PyPDF2 for text-based PDFs
        2. Fall back to Azure OCR for scanned PDFs
        """
        result = {
            'text': '',
            'pages': [],
            'method': 'none',
            'success': False,
            'error': None
        }
        
        try:
            # First try PyPDF2 for text-based PDFs
            text, pages = self._extract_with_pypdf2(pdf_path)
            if text and len(text.strip()) > 100:  # Minimum text threshold
                result['text'] = text
                result['pages'] = pages
                result['method'] = 'pypdf2'
                result['success'] = True
                return result
            
            # If PyPDF2 fails or returns minimal text, use Azure OCR
            if self.client:
                text, pages = self._extract_with_azure_ocr(pdf_path)
                if text:
                    result['text'] = text
                    result['pages'] = pages
                    result['method'] = 'azure_ocr'
                    result['success'] = True
                    return result
            else:
                result['error'] = 'Azure OCR not configured and PDF appears to be scanned'
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _extract_with_pypdf2(self, pdf_path: str) -> tuple:
        """Extract text using PyPDF2"""
        text = ""
        pages = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n\n"
                    pages.append({
                        'page_number': page_num + 1,
                        'text': page_text
                    })
                    
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
            
        return text, pages
    
    def _extract_with_azure_ocr(self, pdf_path: str) -> tuple:
        """Extract text using Azure Computer Vision OCR"""
        text = ""
        pages = []
        
        try:
            # Convert PDF to images
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(pdf_path, dpi=300)
                
                for i, image in enumerate(images):
                    # Convert PIL Image to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    
                    # Perform OCR
                    page_text = self._ocr_image(img_byte_arr)
                    text += page_text + "\n\n"
                    pages.append({
                        'page_number': i + 1,
                        'text': page_text
                    })
                    
        except Exception as e:
            print(f"Azure OCR extraction error: {e}")
            
        return text, pages
    
    def _ocr_image(self, image_stream: io.BytesIO) -> str:
        """Perform OCR on a single image"""
        try:
            # Call Azure Read API
            read_response = self.client.read_in_stream(
                image_stream,
                raw=True
            )
            
            # Get operation location
            read_operation_location = read_response.headers["Operation-Location"]
            operation_id = read_operation_location.split("/")[-1]
            
            # Wait for the operation to complete
            while True:
                read_result = self.client.get_read_result(operation_id)
                if read_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)
            
            # Extract text
            text = ""
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        text += line.text + "\n"
                        
            return text
            
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from a single image file"""
        try:
            with open(image_path, "rb") as image_stream:
                return self._ocr_image(image_stream)
        except Exception as e:
            print(f"Image OCR error: {e}")
            return ""