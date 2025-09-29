"""
PDF Processing Module
Extracts and processes text content from PDF files for RAG system
"""

import os
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path

# PDF processing libraries
import PyPDF2
import pdfplumber
import pymupdf as fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction, cleaning, and chunking for RAG"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\\n\\n", "\\n", " ", ""]
        )
        
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 (fast but basic)"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\\n[Page {page_num + 1}]\\n{page_text}\\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num + 1}: {e}")
                        continue
            return text
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (better for complex layouts)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += f"\\n[Page {page_num + 1}]\\n{page_text}\\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num + 1}: {e}")
                        continue
            return text
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""
    
    def extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (best for preserving formatting)"""
        try:
            text = ""
            pdf_document = fitz.open(pdf_path)
            for page_num in range(pdf_document.page_count):
                try:
                    page = pdf_document[page_num]
                    page_text = page.get_text()
                    if page_text.strip():
                        text += f"\\n[Page {page_num + 1}]\\n{page_text}\\n"
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num + 1}: {e}")
                    continue
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str, method: str = "auto") -> str:
        """
        Extract text from PDF using specified method or auto-select best method
        
        Args:
            pdf_path: Path to PDF file
            method: "auto", "pypdf2", "pdfplumber", or "pymupdf"
        
        Returns:
            Extracted text content
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return ""
        
        if method == "auto":
            # Try methods in order of preference
            methods = [
                ("pymupdf", self.extract_text_pymupdf),
                ("pdfplumber", self.extract_text_pdfplumber),
                ("pypdf2", self.extract_text_pypdf2)
            ]
            
            for method_name, extract_func in methods:
                logger.info(f"Trying {method_name} for {pdf_path}")
                text = extract_func(pdf_path)
                if text and len(text.strip()) > 100:  # Reasonable amount of text
                    logger.info(f"Successfully extracted text using {method_name}")
                    return text
            
            logger.warning("All extraction methods failed or produced minimal text")
            return ""
        
        elif method == "pypdf2":
            return self.extract_text_pypdf2(pdf_path)
        elif method == "pdfplumber":
            return self.extract_text_pdfplumber(pdf_path)
        elif method == "pymupdf":
            return self.extract_text_pymupdf(pdf_path)
        else:
            logger.error(f"Unknown extraction method: {method}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove page markers and headers/footers that might be noise
        text = re.sub(r'\[Page \d+\]\s*', '', text)
        text = re.sub(r'Page\s*\d+\s*of\s*\d+', '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace but preserve paragraph structure
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple line breaks to double
        
        # Fix common PDF extraction issues
        text = text.replace('\u2019', "'")  # Smart apostrophe
        text = text.replace('\u201c', '"')  # Smart quote left
        text = text.replace('\u201d', '"')  # Smart quote right
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '--') # Em dash
        text = text.replace('\xa0', ' ')     # Non-breaking space
        text = text.replace('\x0c', '')      # Form feed
        
        # Remove lines that are likely headers/footers/page numbers
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            
            # Skip empty lines or very short lines
            if len(line) < 5:
                continue
                
            # Skip lines that are just numbers (page numbers)
            if re.match(r'^\d+$', line):
                continue
                
            # Skip lines with very few letters (likely formatting)
            letter_count = sum(1 for c in line if c.isalpha())
            if letter_count < len(line) * 0.3 and len(line) > 10:
                continue
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Document]:
        """Split text into chunks for RAG processing"""
        if not text:
            return []
        
        # Clean text first
        clean_text = self.clean_text(text)
        
        # Create Document object
        doc = Document(page_content=clean_text, metadata=metadata or {})
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        # Filter out poor quality chunks (too short, mostly numbers/symbols, etc.)
        quality_chunks = []
        for i, chunk in enumerate(chunks):
            content = chunk.page_content.strip()
            
            # Skip chunks that are too short or mostly non-alphabetic
            if len(content) < 50:  # Skip very short chunks
                continue
                
            # Count alphabetic characters
            alpha_chars = sum(1 for c in content if c.isalpha())
            if alpha_chars < len(content) * 0.3:  # Skip if less than 30% alphabetic
                continue
            
            # Skip chunks that are mostly page numbers or headers
            if re.match(r'^\s*\[?Page\s*\d+\]?\s*$', content, re.IGNORECASE):
                continue
                
            chunk.metadata.update({
                'chunk_id': len(quality_chunks),
                'chunk_count': len(chunks),
                'source_type': 'pdf',
                'content_length': len(content)
            })
            
            quality_chunks.append(chunk)
        
        logger.info(f"Filtered {len(chunks)} chunks to {len(quality_chunks)} quality chunks")
        return quality_chunks
    
    def process_pdf(self, pdf_path: str, metadata: Dict = None) -> List[Document]:
        """
        Complete PDF processing pipeline: extract, clean, and chunk text
        
        Args:
            pdf_path: Path to PDF file
            metadata: Additional metadata to include with chunks
        
        Returns:
            List of Document chunks ready for embedding
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error(f"No text extracted from {pdf_path}")
            return []
        
        # Log sample of extracted text for debugging
        sample_text = text[:500].replace('\n', ' ')
        logger.info(f"Sample extracted text: {sample_text}...")
        
        # Prepare metadata
        file_metadata = {
            'source': pdf_path,
            'filename': Path(pdf_path).name,
            'file_type': 'pdf',
            'character_count': len(text),
            'word_count': len(text.split())
        }
        
        # Handle PDF metadata - convert complex objects to strings
        pdf_info = self.get_pdf_info(pdf_path)
        if 'metadata' in pdf_info and pdf_info['metadata']:
            # Convert PDF metadata to simple key-value pairs
            pdf_meta = pdf_info['metadata']
            for key, value in pdf_meta.items():
                # Convert complex objects to strings and clean key names
                clean_key = key.lstrip('/').lower().replace(' ', '_')
                if isinstance(value, (str, int, float, bool)):
                    file_metadata[f'pdf_{clean_key}'] = value
                else:
                    file_metadata[f'pdf_{clean_key}'] = str(value)
        
        # Add other PDF info as simple types
        if 'page_count' in pdf_info:
            file_metadata['page_count'] = pdf_info['page_count']
        if 'file_size' in pdf_info:
            file_metadata['file_size_bytes'] = pdf_info['file_size']
        
        if metadata:
            file_metadata.update(metadata)
        
        # Chunk text
        chunks = self.chunk_text(text, file_metadata)
        
        logger.info(f"Successfully processed {pdf_path}: {len(chunks)} chunks created")
        return chunks
    
    def get_pdf_info(self, pdf_path: str) -> Dict:
        """Get basic information about a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Convert metadata to simple types
                simple_metadata = {}
                if pdf_reader.metadata:
                    for key, value in pdf_reader.metadata.items():
                        # Clean key name
                        clean_key = str(key).strip().lstrip('/').lower().replace(' ', '_')
                        # Convert value to simple type
                        if isinstance(value, (str, int, float, bool)):
                            simple_metadata[clean_key] = value
                        else:
                            simple_metadata[clean_key] = str(value)
                
                info = {
                    'filename': Path(pdf_path).name,
                    'file_size': os.path.getsize(pdf_path),
                    'page_count': len(pdf_reader.pages),
                    'metadata': simple_metadata
                }
                
                return info
        except Exception as e:
            logger.error(f"Failed to get PDF info: {e}")
            return {'filename': Path(pdf_path).name, 'error': str(e)}
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate that file is a readable PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Try to read first page
                if len(pdf_reader.pages) > 0:
                    pdf_reader.pages[0].extract_text()
                return True
        except Exception as e:
            logger.error(f"PDF validation failed: {e}")
            return False

# Global processor instance
pdf_processor = PDFProcessor()