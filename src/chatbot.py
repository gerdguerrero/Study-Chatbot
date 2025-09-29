"""
Main Chatbot Class
Integrates RAG system, PDF processing, and exam generation
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import os

from config import settings, validate_openai_key
from rag_system import get_rag_system
from pdf_processor import pdf_processor
from exam_generator import get_exam_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudyChatbot:
    """Main chatbot class that coordinates all AI functionalities"""
    
    def __init__(self):
        """Initialize the study chatbot with all components"""
        
        # Validate setup
        if not validate_openai_key():
            raise ValueError("OpenAI API key required. Please set OPENAI_API_KEY environment variable.")
        
        # Initialize components
        self.rag_system = get_rag_system()
        self.exam_generator = get_exam_generator()
        
        # Chat history
        self.chat_history = []
        
        # Document tracking
        self.uploaded_documents = {}
        
        logger.info("Study chatbot initialized successfully")
    
    def upload_pdf(self, pdf_path: str, custom_metadata: Dict = None) -> Dict:
        """
        Upload and process a PDF document
        
        Args:
            pdf_path: Path to PDF file
            custom_metadata: Additional metadata for the document
        
        Returns:
            Upload result with status and information
        """
        try:
            logger.info(f"Uploading PDF: {pdf_path}")
            
            # Validate file
            if not os.path.exists(pdf_path):
                return {"success": False, "error": "File not found"}
            
            if not pdf_processor.validate_pdf(pdf_path):
                return {"success": False, "error": "Invalid or corrupted PDF file"}
            
            # Get PDF info
            pdf_info = pdf_processor.get_pdf_info(pdf_path)
            
            # Check file size (convert bytes to MB)
            file_size_mb = pdf_info.get('file_size', 0) / (1024 * 1024)
            if file_size_mb > settings.max_file_size_mb:
                return {
                    "success": False, 
                    "error": f"File too large ({file_size_mb:.1f}MB). Maximum size: {settings.max_file_size_mb}MB"
                }
            
            # Prepare metadata
            metadata = {
                "upload_method": "chatbot",
                "file_size_mb": file_size_mb,
                **pdf_info
            }
            
            if custom_metadata:
                metadata.update(custom_metadata)
            
            # Add to RAG system
            success = self.rag_system.add_pdf(pdf_path, metadata)
            
            if success:
                # Track uploaded document
                doc_id = Path(pdf_path).stem
                self.uploaded_documents[doc_id] = {
                    "path": pdf_path,
                    "metadata": metadata,
                    "upload_time": pdf_info.get('upload_time', 'unknown')
                }
                
                return {
                    "success": True,
                    "message": f"Successfully uploaded {pdf_info['filename']}",
                    "document_info": {
                        "filename": pdf_info['filename'],
                        "pages": pdf_info.get('page_count', 0),
                        "size_mb": file_size_mb,
                        "document_id": doc_id
                    }
                }
            else:
                return {"success": False, "error": "Failed to process PDF content"}
            
        except Exception as e:
            logger.error(f"Failed to upload PDF: {e}")
            return {"success": False, "error": str(e)}
    
    def ask_question(self, question: str) -> Dict:
        """
        Ask a question and get an AI response using RAG
        
        Args:
            question: User's question
        
        Returns:
            Response with answer, sources, and metadata
        """
        try:
            logger.info(f"Processing question: {question[:100]}...")
            
            # Get response using RAG
            response = self.rag_system.ask_question(question, self.chat_history)
            
            # Add to chat history
            chat_entry = {
                "question": question,
                "answer": response.get("answer", ""),
                "sources": response.get("sources", []),
                "has_context": response.get("has_context", False)
            }
            
            self.chat_history.append(chat_entry)
            
            # Limit chat history length
            if len(self.chat_history) > settings.max_history_length:
                self.chat_history.pop(0)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process question: {e}")
            return {
                "answer": f"I encountered an error: {str(e)}",
                "sources": [],
                "has_context": False,
                "error": str(e)
            }
    
    def generate_exam(self, exam_config: Dict = None) -> Dict:
        """
        Generate a practice exam from uploaded documents
        
        Args:
            exam_config: Configuration for question types and counts
        
        Returns:
            Generated exam
        """
        try:
            logger.info("Generating practice exam")
            
            # Check if documents are uploaded
            if not self.uploaded_documents:
                return {
                    "success": False,
                    "error": "No documents uploaded. Please upload study materials first."
                }
            
            # Get context from documents using subject-specific targeted queries
            # Prioritize technical content over administrative/standards content
            context_queries = [
                "testing methods techniques procedures processes",  # Core technical content
                "equipment tools instruments technology",          # Technical equipment
                "defects flaws inspection evaluation",             # Core inspection topics
                "applications materials components specimens"       # Practical applications
            ]
            
            # Also try to identify the main subject from a sample of content
            sample_context = self.rag_system.get_relevant_context(
                "main topic subject matter focus", 
                max_tokens=500
            )
            
            # Extract subject-specific terms if possible
            subject_keywords = []
            if sample_context:
                # Look for domain-specific keywords in the sample
                common_terms = ["NDT", "non-destructive", "testing", "ultrasonic", "radiographic", 
                              "magnetic particle", "penetrant", "eddy current", "visual inspection"]
                subject_keywords = [term for term in common_terms if term.lower() in sample_context.lower()]
            
            # Add subject-specific queries if we identified the domain
            if subject_keywords:
                context_queries.insert(0, f"{' '.join(subject_keywords[:3])} methods principles")
            
            all_context = []
            for query in context_queries:
                context_chunk = self.rag_system.get_relevant_context(
                    query, 
                    max_tokens=1500  # Smaller chunks for each query
                )
                if context_chunk:
                    all_context.append(context_chunk)
            
            # Combine all context with clear separation
            context = "\n\n=== TECHNICAL CONTENT SECTION ===\n\n".join(all_context) if all_context else None
            
            if not context or len(context.strip()) < 100:
                return {
                    "success": False,
                    "error": "Could not extract sufficient content from uploaded documents. Please ensure your PDFs contain readable text and try uploading again."
                }
            
            # Generate exam
            exam = self.exam_generator.generate_complete_exam(context, exam_config)
            
            if exam.get("sections"):
                # Create formatted versions
                formatted_exam = self.exam_generator.format_exam_for_display(exam)
                formatted_answers = self.exam_generator.format_answers_for_display(exam)
                
                return {
                    "success": True,
                    "exam": exam,
                    "exam_data": exam.get("sections", {}),  # Structured data for UI
                    "formatted_exam": formatted_exam,      # Questions only
                    "formatted_answers": formatted_answers  # Complete answer key
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate exam questions from the uploaded content."
                }
            
        except Exception as e:
            logger.error(f"Failed to generate exam: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_chat_history(self) -> List[Dict]:
        """Get the current chat history"""
        return self.chat_history.copy()
    
    def clear_chat_history(self) -> bool:
        """Clear the chat history"""
        try:
            self.chat_history.clear()
            logger.info("Chat history cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")
            return False
    
    def get_uploaded_documents(self) -> Dict:
        """Get information about uploaded documents"""
        return self.uploaded_documents.copy()
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        try:
            db_info = self.rag_system.get_database_info()
            
            return {
                "openai_api": "connected" if validate_openai_key() else "not_configured",
                "rag_system": "active",
                "documents_in_db": db_info.get("document_count", 0),
                "uploaded_files": len(self.uploaded_documents),
                "chat_history_length": len(self.chat_history),
                "exam_generator": "ready"
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def reset_system(self) -> bool:
        """Reset the entire system (clear documents and history)"""
        try:
            logger.info("Resetting system")
            
            # Clear chat history
            self.chat_history.clear()
            
            # Clear uploaded documents tracking
            self.uploaded_documents.clear()
            
            # Reset RAG database
            success = self.rag_system.reset_database()
            
            if success:
                logger.info("System reset successfully")
                return True
            else:
                logger.error("Failed to reset RAG database")
                return False
            
        except Exception as e:
            logger.error(f"Failed to reset system: {e}")
            return False

# Global chatbot instance
def get_chatbot() -> StudyChatbot:
    """Get or create global chatbot instance"""
    if not hasattr(get_chatbot, "_instance"):
        get_chatbot._instance = StudyChatbot()
    return get_chatbot._instance