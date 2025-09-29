# 🚀 Quick Start Guide

## Setup Instructions

1. **Set your OpenAI API Key**:
   - Open the `.env` file in the project root
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - Get your API key from: https://platform.openai.com/api-keys

2. **Run the Application**:
   ```bash
   # Activate virtual environment (if not already active)
   .venv\Scripts\activate
   
   # Start the chatbot
   streamlit run src/app.py
   ```

3. **Use the Chatbot**:
   - Open your browser to the displayed URL (usually http://localhost:8501)
   - Upload your PDF study materials using the sidebar
   - Ask questions about your documents
   - Generate practice exams

## Example Usage

### Upload Documents
- Click "Browse files" in the sidebar
- Upload your academic PDFs (textbooks, papers, notes)
- Wait for processing confirmation

### Ask Questions
- "Explain machine learning algorithms from my textbook"
- "What are the main concepts in Chapter 3?"
- "Summarize the research methodology section"

### Generate Exams
- Go to the "Generate Exam" tab
- Choose question types and quantities
- Click "Generate Practice Exam"
- Download or copy the exam

## Features

✅ **Real AI Integration**: Uses OpenAI GPT models for understanding and responses
✅ **RAG Technology**: Retrieval Augmented Generation for document-based answers
✅ **PDF Processing**: Extracts and processes text from academic documents
✅ **Smart Chunking**: Intelligently splits documents for better retrieval
✅ **Vector Search**: Semantic search through your document content
✅ **Exam Generation**: Creates multiple choice, T/F, short answer, and essay questions
✅ **Chat History**: Maintains conversation context
✅ **Source Citations**: Shows which documents were used for answers

## Troubleshooting

**OpenAI API Error**: Make sure your API key is correctly set in the `.env` file

**PDF Upload Issues**: Ensure PDFs are text-based (not scanned images)

**Empty Responses**: Upload relevant documents before asking questions

**Dependencies Issues**: Run the setup test: `python test_setup.py`

---

🎯 **You now have a fully functional AI study assistant with real NLP, RAG, and exam generation capabilities!**