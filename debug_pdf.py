"""
PDF Debug Script - Test PDF processing with your specific files
"""
import os
import sys
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_processor import PDFProcessor
from config import settings

def test_pdf_processing():
    print("🔍 PDF Processing Debug Test")
    print("=" * 50)
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Test with sample files (you can replace with your actual file paths)
    test_files = [
        # Add paths to your problematic PDFs here
        # "path/to/LM8_Acoustic Emission.pdf",
        # "path/to/LM7_Ultrasonic.pdf"
    ]
    
    # If no specific files provided, look for PDFs in current directory
    if not test_files:
        current_dir = os.getcwd()
        pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.pdf')]
        test_files = [os.path.join(current_dir, f) for f in pdf_files[:2]]  # Test first 2 PDFs
        
        if not test_files:
            print("❌ No PDF files found in current directory")
            print("Please place some PDF files in the project directory or update the test_files list")
            return
    
    for pdf_path in test_files:
        print(f"\n📄 Testing: {os.path.basename(pdf_path)}")
        print("-" * 40)
        
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            continue
            
        # Test validation
        try:
            is_valid = processor.validate_pdf(pdf_path)
            print(f"✅ PDF Validation: {'PASSED' if is_valid else 'FAILED'}")
        except Exception as e:
            print(f"❌ PDF Validation Error: {e}")
            traceback.print_exc()
            continue
            
        # Test info extraction
        try:
            pdf_info = processor.get_pdf_info(pdf_path)
            print(f"📊 PDF Info: {pdf_info}")
        except Exception as e:
            print(f"❌ PDF Info Error: {e}")
            
        # Test text extraction methods
        methods = ["pypdf2", "pdfplumber", "pymupdf"]
        
        for method in methods:
            try:
                print(f"\n🔧 Testing {method}:")
                
                if method == "pypdf2":
                    text = processor.extract_text_pypdf2(pdf_path)
                elif method == "pdfplumber":
                    text = processor.extract_text_pdfplumber(pdf_path)
                elif method == "pymupdf":
                    text = processor.extract_text_pymupdf(pdf_path)
                
                if text:
                    print(f"   ✅ {method}: {len(text)} characters extracted")
                    print(f"   📝 First 200 chars: {text[:200]!r}")
                else:
                    print(f"   ❌ {method}: No text extracted")
                    
            except Exception as e:
                print(f"   💥 {method} ERROR: {e}")
                traceback.print_exc()
                
        # Test full processing pipeline
        try:
            print(f"\n🚀 Testing full processing pipeline:")
            chunks = processor.process_pdf(pdf_path)
            
            if chunks:
                print(f"   ✅ Success: {len(chunks)} chunks created")
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    print(f"   📄 Chunk {i}: {len(chunk.page_content)} chars")
                    print(f"      Metadata: {chunk.metadata}")
                    print(f"      Preview: {chunk.page_content[:100]!r}")
            else:
                print(f"   ❌ No chunks created")
                
        except Exception as e:
            print(f"   💥 Pipeline ERROR: {e}")
            traceback.print_exc()
            
        print("\n" + "=" * 50)

if __name__ == "__main__":
    test_pdf_processing()