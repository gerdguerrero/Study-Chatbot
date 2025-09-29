"""
Configuration settings for AI Study Chatbot
Handles API keys, database settings, and application configuration
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"
    
    # RAG Configuration
    chroma_persist_directory: str = "./embeddings"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens_per_chunk: int = 500
    
    # Document Processing
    documents_directory: str = "./documents"
    supported_file_types: list = [".pdf", ".txt", ".docx"]
    max_file_size_mb: int = 50
    
    # Chatbot Settings
    max_history_length: int = 10
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Exam Generation
    default_exam_questions: int = 5
    question_types: list = ["multiple_choice", "true_false", "short_answer", "essay"]
    
    # UI Settings
    page_title: str = "AI Study Assistant"
    page_icon: str = "🤖"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

def validate_openai_key() -> bool:
    """Validate that OpenAI API key is provided and not empty"""
    if not settings.openai_api_key:
        return False
    return True

def get_openai_headers() -> dict:
    """Get headers for OpenAI API requests"""
    return {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }

# Environment file template
ENV_TEMPLATE = """# AI Study Chatbot Environment Variables
# Copy this to .env and fill in your actual values

# Required: Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Model configurations
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Optional: Storage directories
CHROMA_PERSIST_DIRECTORY=./embeddings
DOCUMENTS_DIRECTORY=./documents
"""

def create_env_template():
    """Create .env template file if it doesn't exist"""
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(ENV_TEMPLATE)
        print(f"Created {env_path} template. Please add your OpenAI API key.")
        return True
    return False