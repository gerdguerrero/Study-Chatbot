"""
RAG System Implementation
Retrieval Augmented Generation using ChromaDB and OpenAI embeddings
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np

# RAG and vector database
import chromadb
from chromadb.config import Settings as ChromaSettings
import openai
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from config import settings, validate_openai_key
from pdf_processor import pdf_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    """Retrieval Augmented Generation system using ChromaDB and OpenAI"""
    
    def __init__(self):
        """Initialize RAG system with embeddings and vector database"""
        
        # Validate OpenAI API key
        if not validate_openai_key():
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        openai.api_key = settings.openai_api_key
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_embedding_model
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Initialize vector store with dimension compatibility check
        try:
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name="study_documents",
                embedding_function=self.embeddings
            )
        except Exception as e:
            # If there's a dimension mismatch, reset the collection
            if "dimension" in str(e).lower():
                logger.warning(f"Embedding dimension mismatch detected: {e}")
                logger.info("Resetting vector database to match new embedding model...")
                self._reset_collection()
                self.vector_store = Chroma(
                    client=self.chroma_client,
                    collection_name="study_documents",
                    embedding_function=self.embeddings
                )
            else:
                raise e
        
        logger.info("RAG system initialized successfully")
    
    def _reset_collection(self):
        """Reset the ChromaDB collection to handle embedding dimension changes"""
        try:
            # Try to delete the existing collection
            try:
                collection = self.chroma_client.get_collection("study_documents")
                self.chroma_client.delete_collection("study_documents")
                logger.info("Deleted existing collection with incompatible dimensions")
            except Exception:
                # Collection doesn't exist or already deleted
                pass
            
            # Clear any persistent data
            import shutil
            import os
            if os.path.exists(self.settings.chroma_persist_directory):
                try:
                    shutil.rmtree(self.settings.chroma_persist_directory)
                    os.makedirs(self.settings.chroma_persist_directory, exist_ok=True)
                    logger.info("Cleared ChromaDB persistent directory")
                except Exception as e:
                    logger.warning(f"Could not clear persistent directory: {e}")
            
            # Reinitialize the client
            self.chroma_client = chromadb.PersistentClient(
                path=self.settings.chroma_persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
    
    def _clean_metadata(self, metadata: Dict) -> Dict:
        """Clean metadata to contain only simple types that ChromaDB can handle"""
        cleaned = {}
        for key, value in metadata.items():
            # Convert key to string and clean it
            clean_key = str(key).strip().replace('/', '').replace(' ', '_').lower()
            
            # Only include simple types
            if isinstance(value, (str, int, float, bool)):
                cleaned[clean_key] = value
            elif value is None:
                cleaned[clean_key] = ""
            else:
                # Convert complex objects to strings
                cleaned[clean_key] = str(value)[:500]  # Truncate long strings
        
        return cleaned
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector database"""
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return False
            
            # Clean metadata for ChromaDB compatibility
            cleaned_docs = []
            for doc in documents:
                # Create a new document with cleaned metadata
                cleaned_metadata = self._clean_metadata(doc.metadata)
                cleaned_doc = Document(
                    page_content=doc.page_content,
                    metadata=cleaned_metadata
                )
                cleaned_docs.append(cleaned_doc)
            
            # Add cleaned documents to vector store
            try:
                self.vector_store.add_documents(cleaned_docs)
            except Exception as e:
                # Handle dimension mismatch by resetting collection
                if "dimension" in str(e).lower():
                    logger.warning(f"Embedding dimension mismatch: {e}")
                    logger.info("Resetting vector database and retrying...")
                    self._reset_collection()
                    
                    # Recreate vector store
                    self.vector_store = Chroma(
                        client=self.chroma_client,
                        collection_name="study_documents",
                        embedding_function=self.embeddings
                    )
                    
                    # Retry adding documents
                    self.vector_store.add_documents(cleaned_docs)
                    logger.info("Successfully added documents after collection reset")
                else:
                    raise e
            
            # Log sample of what was added for debugging
            if cleaned_docs:
                sample_doc = cleaned_docs[0]
                sample_content = sample_doc.page_content[:300].replace('\n', ' ')
                logger.info(f"Sample stored content: {sample_content}...")
            
            logger.info(f"Successfully added {len(cleaned_docs)} document chunks to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector database: {e}")
            return False
    
    def add_pdf(self, pdf_path: str, metadata: Dict = None) -> bool:
        """Process and add a PDF to the RAG system"""
        try:
            logger.info(f"Adding PDF to RAG system: {pdf_path}")
            
            # Process PDF into chunks
            chunks = pdf_processor.process_pdf(pdf_path, metadata)
            
            if not chunks:
                logger.error(f"No content extracted from PDF: {pdf_path}")
                return False
            
            # Add chunks to vector database
            return self.add_documents(chunks)
            
        except Exception as e:
            logger.error(f"Failed to add PDF to RAG system: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents using vector similarity"""
        try:
            # Perform similarity search with score to get better quality results
            results_with_scores = self.vector_store.similarity_search_with_relevance_scores(query, k=k*2)
            
            # Filter out results with very low scores (less relevant)
            filtered_results = []
            for doc, score in results_with_scores:
                if score > 0.1:  # Minimum relevance threshold
                    filtered_results.append(doc)
                if len(filtered_results) >= k:
                    break
            
            # If we don't have enough relevant results, fall back to regular search
            if len(filtered_results) < k//2:
                logger.info(f"Low relevance scores, falling back to regular search")
                filtered_results = self.vector_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(filtered_results)} similar documents for query")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def similarity_search_with_scores(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search with similarity scores"""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            logger.info(f"Found {len(results)} similar documents with scores")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search with scores failed: {e}")
            return []
    
    def get_document_overview(self, max_tokens: int = 4000) -> str:
        """Get a representative overview of all documents for broad questions"""
        try:
            # Search for introductory and overview content specifically
            intro_queries = [
                "introduction overview summary definition",
                "objectives goals purpose learning outcomes",
                "abstract conclusion summary",
                "introduction definition what is"
            ]
            
            overview_docs = []
            seen_content = set()
            
            for query in intro_queries:
                docs = self.vector_store.similarity_search(query, k=5)
                for doc in docs:
                    # Avoid duplicate content
                    content_hash = hash(doc.page_content[:200])
                    if content_hash not in seen_content:
                        overview_docs.append(doc)
                        seen_content.add(content_hash)
                if len(overview_docs) >= 15:  # Limit total docs
                    break
            
            # If we don't have enough intro content, get general content
            if len(overview_docs) < 5:
                general_docs = self.vector_store.similarity_search("main content", k=10)
                for doc in general_docs:
                    content_hash = hash(doc.page_content[:200])
                    if content_hash not in seen_content and len(overview_docs) < 15:
                        overview_docs.append(doc)
                        seen_content.add(content_hash)
            
            if not overview_docs:
                return ""
            
            # Prioritize content that looks like introductions or summaries
            def get_intro_score(content):
                intro_keywords = ['introduction', 'overview', 'summary', 'define', 'definition', 
                                'objectives', 'goals', 'purpose', 'outline', 'after this lesson']
                score = 0
                content_lower = content.lower()
                for keyword in intro_keywords:
                    if keyword in content_lower:
                        score += 1
                # Bonus for content at the beginning of document
                if 'page 1' in content_lower or 'introduction' in content_lower:
                    score += 2
                return score
            
            # Sort by intro score (highest first)
            overview_docs.sort(key=lambda doc: get_intro_score(doc.page_content), reverse=True)
            
            # Build overview prioritizing high-scoring content
            overview_parts = []
            token_count = 0
            
            for doc in overview_docs:
                content = doc.page_content
                source = doc.metadata.get('filename', 'Document')
                
                estimated_tokens = len(content) // 4
                if token_count + estimated_tokens > max_tokens:
                    remaining_chars = (max_tokens - token_count) * 4
                    if remaining_chars > 200:
                        content = content[:remaining_chars] + "..."
                        overview_parts.append(f"[From: {source}]\n{content}")
                    break
                
                overview_parts.append(f"[From: {source}]\n{content}")
                token_count += estimated_tokens
            
            return "\n\n=== DOCUMENT SECTION ===\n\n".join(overview_parts)
            
        except Exception as e:
            logger.error(f"Failed to get document overview: {e}")
            return ""

    def get_relevant_context(self, query: str, max_tokens: int = 3000) -> str:
        """Get relevant context for a query, respecting token limits"""
        try:
            # Search for relevant documents
            docs = self.similarity_search(query, k=10)  # Get more docs initially
            
            context_parts = []
            token_count = 0
            
            for doc in docs:
                content = doc.page_content
                source = doc.metadata.get('filename', 'Unknown source')
                
                # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                estimated_tokens = len(content) // 4
                
                if token_count + estimated_tokens > max_tokens:
                    # Add partial content if it fits
                    remaining_chars = (max_tokens - token_count) * 4
                    if remaining_chars > 100:  # Only add if meaningful amount
                        content = content[:remaining_chars] + "..."
                        context_parts.append(f"[From: {source}]\\n{content}")
                    break
                
                context_parts.append(f"[From: {source}]\\n{content}")
                token_count += estimated_tokens
            
            return "\\n\\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return ""
    
    def ask_question(self, question: str, chat_history: List[Dict] = None) -> Dict:
        """
        Answer a question using RAG (Retrieval Augmented Generation)
        
        Args:
            question: User's question
            chat_history: Previous conversation context
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            logger.info(f"Processing question: {question[:100]}...")
            
            # Detect if this is a broad overview question
            overview_keywords = [
                "what is", "tell me about", "describe", "overview", "summary", 
                "about the file", "content of", "main topic", "what does", "explain the document",
                "document all about", "summarize", "what does this cover", "main subject",
                "what are we learning", "course content", "lecture about"
            ]
            
            is_overview_question = any(keyword in question.lower() for keyword in overview_keywords)
            
            if is_overview_question:
                # For broad questions, get document overview
                context = self.get_document_overview(max_tokens=4000)
                logger.info("Using document overview for broad question")
            else:
                # For specific questions, use similarity search
                context = self.get_relevant_context(question, max_tokens=3000)
                logger.info("Using similarity search for specific question")
            
            if not context:
                logger.warning("No relevant context found in documents")
                return {
                    "answer": "I couldn't find relevant information in your uploaded documents to answer this question. Please make sure you've uploaded relevant materials or try rephrasing your question.",
                    "sources": [],
                    "has_context": False
                }
            
            # Prepare conversation history
            messages = []
            
            # Add system prompt - different for overview vs specific questions
            if is_overview_question:
                system_prompt = f"""You are a helpful AI study assistant. The user is asking for an overview of their uploaded document(s). Analyze the content below and provide a comprehensive summary.

Document Content:
{context}

Instructions:
1. Identify the main subject/topic of the document(s)
2. Summarize the key themes and concepts covered
3. Highlight important sections or chapters
4. Mention specific topics, methods, or areas discussed
5. Be specific about what the document teaches or covers
6. Structure your response clearly with main points
7. Use information directly from the provided content"""
            else:
                system_prompt = f"""You are a helpful AI study assistant. Answer the user's question based on the provided context from their academic documents.
            
Context from uploaded documents:
{context}

Instructions:
1. Answer based primarily on the provided context
2. Be accurate and cite specific information from the documents
3. If the context doesn't fully answer the question, say so
4. Use clear, educational language
5. Structure your response for easy understanding"""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Add chat history if provided
            if chat_history:
                for chat in chat_history[-5:]:  # Last 5 messages for context
                    messages.append({"role": "user", "content": chat.get("question", "")})
                    messages.append({"role": "assistant", "content": chat.get("answer", "")})
            
            # Add current question
            messages.append({"role": "user", "content": question})
            
            # Get response from OpenAI
            response = openai.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            # Extract sources from context
            sources = []
            for line in context.split("\\n"):
                if line.startswith("[From: ") and line.endswith("]"):
                    source = line[7:-1]  # Remove "[From: " and "]"
                    if source not in sources:
                        sources.append(source)
            
            result = {
                "answer": answer,
                "sources": sources,
                "has_context": True,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            logger.info("Successfully generated answer using RAG")
            return result
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "has_context": False,
                "error": str(e)
            }
    
    def get_database_info(self) -> Dict:
        """Get information about the current vector database"""
        try:
            collection = self.chroma_client.get_collection("study_documents")
            count = collection.count()
            
            return {
                "document_count": count,
                "collection_name": "study_documents",
                "embedding_model": settings.openai_embedding_model,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                "document_count": 0,
                "collection_name": "study_documents",
                "status": "error",
                "error": str(e)
            }
    
    def reset_database(self) -> bool:
        """Reset/clear the vector database"""
        try:
            # Delete existing collection
            try:
                self.chroma_client.delete_collection("study_documents")
            except:
                pass  # Collection might not exist
            
            # Recreate vector store
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name="study_documents",
                embedding_function=self.embeddings
            )
            
            logger.info("Successfully reset vector database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False

# Global RAG system instance
def get_rag_system() -> RAGSystem:
    """Get or create global RAG system instance"""
    if not hasattr(get_rag_system, "_instance"):
        get_rag_system._instance = RAGSystem()
    return get_rag_system._instance