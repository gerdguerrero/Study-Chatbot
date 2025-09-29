# 🤖 AI Study Chatbot with RAG & Exam Generation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-green)](https://openai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-orange)](https://chromadb.com)

A powerful AI-powered study assistant that processes your academic PDFs and enables natural conversation about the content using **OpenAI's API** and **RAG (Retrieval Augmented Generation)** technology.

![Study Chatbot Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## ✨ Key Features

- **🤖 Real AI Conversations**: Powered by OpenAI GPT-3.5-turbo for natural language understanding
- **📚 Smart PDF Processing**: Upload and process academic modules, textbooks, research papers
- **🔍 RAG Implementation**: Retrieval Augmented Generation for accurate, document-based responses
- **📝 Intelligent Exam Generation**: Create practice tests with 4 difficulty levels from your materials
- **🎯 Document-Specific Responses**: AI responses based strictly on your uploaded content
- **💬 Natural Language Interface**: Ask questions in plain English about your documents
- **🎓 Educational Focus**: Designed specifically for academic study and learning

## 🚀 Quick Demo

1. **Upload** your study materials (PDFs)
2. **Ask questions** like:
   - "What are the main concepts in this document?"
   - "Explain the key principles of [topic] from my uploaded files"
   - "What does Chapter 3 say about [concept]?"
3. **Generate exams** with customizable difficulty:
   - Easy: Basic recall and definitions
   - Medium: Application and understanding
   - Hard: Analysis and synthesis
   - Expert: Critical thinking and mastery

## 🛠️ Technology Stack

- **AI Engine**: OpenAI API (GPT-3.5-turbo + text-embedding-ada-002)
- **RAG System**: ChromaDB for vector storage with semantic search
- **PDF Processing**: PyMuPDF, pdfplumber, PyPDF2 with intelligent text extraction
- **Backend**: Python with modular architecture
- **Frontend**: Streamlit for intuitive web interface
- **Vector Search**: OpenAI embeddings with similarity search

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 2GB+ RAM recommended for vector processing

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/Study-Chatbot.git
cd Study-Chatbot
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3. Run the Application
```bash
streamlit run src/app.py
```

### 4. Start Learning! 🎓
- Open http://localhost:8501 in your browser
- Upload your study PDFs
- Start asking questions!

## 📁 Project Structure

```
Study-Chatbot/
├── src/
│   ├── app.py              # Streamlit web interface
│   ├── chatbot.py          # Main chatbot orchestration
│   ├── rag_system.py       # RAG implementation with ChromaDB
│   ├── pdf_processor.py    # Advanced PDF text extraction
│   ├── exam_generator.py   # AI-powered exam generation
│   └── config.py           # Configuration management
├── documents/              # Sample documents (optional)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # You are here!
```

## 💡 Usage Examples

### Chat with Your Documents
```
You: "What is this document about?"
AI: "This document is a comprehensive guide to Non-Destructive Testing (NDT) 
     methods, covering ultrasonic testing, radiographic inspection, and 
     magnetic particle testing techniques..."

You: "Generate 5 questions about NDT methods"
AI: Creates targeted multiple-choice, true/false, and essay questions
    based on your specific document content.
```

### Advanced Features
- **Document Overview**: "Summarize the key topics in my uploaded files"
- **Specific Queries**: "What does section 4.2 say about ultrasonic testing?"
- **Comparative Analysis**: "Compare the advantages of different NDT methods"
- **Exam Generation**: Create custom practice tests with answer keys

## 🔧 Configuration Options

### Environment Variables (.env)
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional Customizations
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
CHROMA_PERSIST_DIRECTORY=./embeddings
MAX_FILE_SIZE_MB=50
```

### Exam Generation Settings
- **Question Types**: Multiple choice, True/False, Short answer, Essay
- **Difficulty Levels**: Easy, Medium, Hard, Expert
- **Customizable Counts**: Configure questions per type
- **Answer Keys**: Toggle show/hide functionality

## 🎯 Core AI Capabilities

### RAG (Retrieval Augmented Generation)
1. **Document Ingestion**: Processes PDFs with advanced text extraction
2. **Semantic Chunking**: Intelligent text segmentation for optimal retrieval
3. **Vector Embedding**: OpenAI embeddings for semantic similarity
4. **Contextual Retrieval**: Finds most relevant document sections
5. **Response Generation**: AI responses grounded in your content

### Intelligent Content Processing
- **Multi-format PDF Support**: Handles various PDF types and layouts
- **Content Quality Filtering**: Removes headers, footers, and noise
- **Subject-Specific Queries**: Optimizes retrieval for technical content
- **Overview Generation**: Synthesizes document summaries

## 🚨 Known Limitations

- **PDF-only Support**: Currently limited to PDF documents
- **English Language**: Optimized for English-language content
- **OpenAI Dependency**: Requires active OpenAI API subscription
- **Single Session**: No persistent user accounts (yet)

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- [ ] Support for more document formats (DOCX, TXT)
- [ ] Multi-language support
- [ ] User authentication and session persistence
- [ ] Advanced analytics and usage tracking
- [ ] Collaborative study features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT and embedding APIs
- **ChromaDB** for the vector database solution
- **Streamlit** for the amazing web framework
- **LangChain** for RAG implementation patterns

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Study-Chatbot/issues)
- **Documentation**: Check the wiki for advanced usage
- **Discussions**: Share your use cases and get help

---

**⭐ Star this repository if it helps with your studies!**

*Built with ❤️ for students and educators worldwide*