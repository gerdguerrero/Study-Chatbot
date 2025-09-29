"""
Streamlit Web Interface for AI Study Chatbot
Main application with file upload, chat interface, and exam generation
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import logging

# Import chatbot components
from config import settings, create_env_template, validate_openai_key
from chatbot import get_chatbot

# Configure page
st.set_page_config(
    page_title=settings.page_title,
    page_icon=settings.page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Early session state initialization to prevent AttributeErrors
def ensure_session_state():
    """Ensure session state is initialized before any access"""
    if 'current_exam' not in st.session_state:
        st.session_state.current_exam = None
    if 'show_answers' not in st.session_state:
        st.session_state.show_answers = False

def initialize_session_state():
    """Initialize session state variables"""
    ensure_session_state()  # Call early initialization first
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}

def check_openai_setup():
    """Check if OpenAI API key is properly configured"""
    if not validate_openai_key():
        st.error("⚠️ OpenAI API key not found!")
        st.markdown("""
        **To get started:**
        1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Create a `.env` file in your project root
        3. Add: `OPENAI_API_KEY=your_key_here`
        
        Or set it as an environment variable.
        """)
        
        # Offer to create .env template
        if st.button("📝 Create .env Template", help="Create a template .env file"):
            if create_env_template():
                st.success("✅ Created `.env` template file! Please add your OpenAI API key.")
                st.rerun()
            else:
                st.error("❌ Failed to create .env template")
        
        return False
    return True

def get_or_create_chatbot():
    """Get existing chatbot or create new one"""
    if st.session_state.chatbot is None:
        try:
            st.session_state.chatbot = get_chatbot()
            logger.info("Initialized chatbot successfully")
        except Exception as e:
            st.error(f"❌ Failed to initialize chatbot: {str(e)}")
            return None
    
    return st.session_state.chatbot

def sidebar_controls():
    """Sidebar with app controls and info"""
    with st.sidebar:
        st.title("🤖 AI Study Assistant")
        st.markdown("Upload PDFs, chat, and generate practice exams!")
        
        # System status
        st.markdown("### 📊 System Status")
        chatbot = st.session_state.get('chatbot')
        if chatbot:
            try:
                status = chatbot.get_system_status()
                st.success(f"✅ API: {status.get('openai_api', 'unknown')}")
                st.info(f"📚 Documents: {status.get('documents_in_db', 0)}")
                st.info(f"💬 Chat entries: {status.get('chat_history_length', 0)}")
            except:
                st.warning("⚠️ System status unavailable")
        else:
            st.warning("⚠️ Chatbot not initialized")
        
        st.markdown("---")
        
        # Controls
        st.markdown("### 🔧 Controls")
        if st.button("🗑️ Clear Chat History", help="Clear all chat history"):
            chatbot = st.session_state.get('chatbot')
            if chatbot and chatbot.clear_chat_history():
                st.session_state.chat_history = []
                st.success("✅ Chat history cleared")
                st.rerun()
        
        if st.button("🔄 Reset System", help="Clear all data and restart"):
            if st.session_state.get('chatbot'):
                st.session_state.chatbot = None
            st.session_state.chat_history = []
            st.session_state.uploaded_files = {}
            st.session_state.current_exam = None
            st.success("✅ System reset")
            st.rerun()
        
        # File upload info
        if st.session_state.uploaded_files:
            st.markdown("### 📁 Uploaded Files")
            for filename, info in st.session_state.uploaded_files.items():
                st.caption(f"📄 {filename} ({info.get('pages', 0)} pages)")
        
        # App info
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("AI Study Chatbot v1.0")
        st.caption("Powered by OpenAI & RAG")

def file_upload_section():
    """File upload interface"""
    st.markdown("## 📂 Upload Study Materials")
    st.markdown("Upload PDF files to build your personalized study database.")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload academic PDFs, textbooks, or study materials"
    )
    
    if uploaded_files:
        chatbot = get_or_create_chatbot()
        if not chatbot:
            return
        
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_files:
                
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    
                    try:
                        # Upload to chatbot
                        result = chatbot.upload_pdf(tmp_path)
                        
                        if result["success"]:
                            # Store in session state
                            st.session_state.uploaded_files[uploaded_file.name] = result["document_info"]
                            
                            st.success(f"✅ Successfully processed **{uploaded_file.name}**")
                            st.info(f"📄 {result['document_info']['pages']} pages • "
                                   f"{result['document_info']['size_mb']:.1f} MB")
                        else:
                            st.error(f"❌ Failed to process {uploaded_file.name}: {result['error']}")
                    
                    finally:
                        # Clean up temp file
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass

def chat_interface():
    """Main chat interface"""
    st.markdown("## 💬 Ask Questions About Your Documents")
    
    # Check if documents are uploaded
    if not st.session_state.uploaded_files:
        st.info("📥 Upload PDF documents first to start chatting about their content.")
        return
    
    # Chat input
    user_question = st.chat_input("Ask a question about your uploaded documents...")
    
    if user_question:
        chatbot = get_or_create_chatbot()
        if not chatbot:
            return
        
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        with st.spinner("🤔 Thinking..."):
            response = chatbot.ask_question(user_question)
        
        # Add assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response.get("sources", []),
            "has_context": response.get("has_context", False)
        })
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                # Show sources if available
                if message.get("sources"):
                    with st.expander("📚 Sources", expanded=False):
                        for j, source in enumerate(message["sources"][:3]):  # Limit to 3 sources
                            st.caption(f"**Source {j+1}:** {source}")
                
                # Indicate if response used document context
                if message.get("has_context"):
                    st.caption("✅ *Response based on your uploaded documents*")
                else:
                    st.caption("ℹ️ *General knowledge response - no relevant context found*")

def display_exam_with_answers(exam_result):
    """Display exam with toggle for showing/hiding answers"""
    st.markdown("## 🎯 Practice Exam")
    
    # Toggle button for answers
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("👁️ Toggle Answers" if not st.session_state.show_answers else "🙈 Hide Answers"):
            st.session_state.show_answers = not st.session_state.show_answers
            st.rerun()
    
    with col2:
        st.download_button(
            label="⬇️ Download Exam",
            data=exam_result.get("formatted_exam", "No exam content"),
            file_name="practice_exam.txt",
            mime="text/plain",
            help="Download exam questions without answers"
        )
    
    st.markdown("---")
    
    # Display the exam content
    show_answers = getattr(st.session_state, 'show_answers', False)
    if show_answers:
        display_exam_with_answer_key(exam_result)
    else:
        display_exam_questions_only(exam_result)

def display_exam_questions_only(exam_result):
    """Display only the exam questions for taking the test"""
    st.markdown("## 📋 Practice Exam")
    st.info("📝 **Instructions:** Answer all questions, then click 'Toggle Answers' to check your responses.")
    
    # Parse and display questions from the exam data
    if "exam_data" in exam_result and exam_result["exam_data"]:
        question_num = 1
        sections = exam_result["exam_data"]
        
        # Multiple Choice Questions
        if "multiple_choice" in sections and sections["multiple_choice"]:
            st.markdown("### Multiple Choice Questions")
            mcq_section = sections["multiple_choice"]
            for mcq in mcq_section.get("questions", []):
                st.markdown(f"**{question_num}. {mcq['question']}**")
                for choice_key, choice_text in mcq["choices"].items():
                    st.markdown(f"   {choice_key}. {choice_text}")
                st.markdown("")  # Add spacing
                question_num += 1
        
        # True/False Questions
        if "true_false" in sections and sections["true_false"]:
            st.markdown("### True/False Questions")
            tf_section = sections["true_false"]
            for tf in tf_section.get("questions", []):
                st.markdown(f"**{question_num}. {tf['statement']}**")
                st.markdown("   ✅ True     ❌ False")
                st.markdown("")  # Add spacing
                question_num += 1
        
        # Short Answer Questions
        if "short_answer" in sections and sections["short_answer"]:
            st.markdown("### Short Answer Questions")
            sa_section = sections["short_answer"]
            for sa in sa_section.get("questions", []):
                st.markdown(f"**{question_num}. {sa['question']}**")
                st.markdown("   ___________________________________________________")
                st.markdown("")  # Add spacing
                question_num += 1
        
        # Essay Questions  
        if "essay" in sections and sections["essay"]:
            st.markdown("### Essay Questions")
            essay_section = sections["essay"]
            for essay in essay_section.get("questions", []):
                st.markdown(f"**{question_num}. {essay['question']}**")
                st.markdown("   " + "_" * 80)
                st.markdown("")  # Add spacing
                question_num += 1
    else:
        st.error("❌ No exam data found")

def display_exam_with_answer_key(exam_result):
    """Display the complete exam with answers"""
    st.markdown("## 📋 Practice Exam with Answer Key")
    st.success("✅ **Answer Key Mode:** Correct answers are shown below each question.")
    
    if "exam_data" in exam_result and exam_result["exam_data"]:
        question_num = 1
        sections = exam_result["exam_data"]
        
        # Multiple Choice Questions with Answers
        if "multiple_choice" in sections and sections["multiple_choice"]:
            st.markdown("### Multiple Choice Questions")
            mcq_section = sections["multiple_choice"]
            for mcq in mcq_section.get("questions", []):
                st.markdown(f"**{question_num}. {mcq['question']}**")
                for choice_key, choice_text in mcq["choices"].items():
                    if choice_key == mcq["correct_answer"]:
                        st.markdown(f"   ✅ **{choice_key}. {choice_text}** *(Correct Answer)*")
                    else:
                        st.markdown(f"   {choice_key}. {choice_text}")
                
                # Show explanation if available
                if "explanation" in mcq:
                    st.info(f"**Explanation:** {mcq['explanation']}")
                
                st.markdown("")
                question_num += 1
        
        # True/False Questions with Answers
        if "true_false" in sections and sections["true_false"]:
            st.markdown("### True/False Questions")
            tf_section = sections["true_false"]
            for tf in tf_section.get("questions", []):
                st.markdown(f"**{question_num}. {tf['statement']}**")
                correct = "True" if tf["correct_answer"] else "False"
                st.markdown(f"   ✅ **Correct Answer:** {correct}")
                
                # Show explanation if available
                if "explanation" in tf:
                    st.info(f"**Explanation:** {tf['explanation']}")
                
                st.markdown("")
                question_num += 1
        
        # Short Answer Questions with Answers
        if "short_answer" in sections and sections["short_answer"]:
            st.markdown("### Short Answer Questions")
            sa_section = sections["short_answer"]
            for sa in sa_section.get("questions", []):
                st.markdown(f"**{question_num}. {sa['question']}**")
                st.success(f"**Sample Answer:** {sa.get('answer', 'Answer not provided')}")
                st.markdown("")
                question_num += 1
        
        # Essay Questions with Answers
        if "essay" in sections and sections["essay"]:
            st.markdown("### Essay Questions")
            essay_section = sections["essay"]
            for essay in essay_section.get("questions", []):
                st.markdown(f"**{question_num}. {essay['question']}**")
                st.success(f"**Key Points:** {essay.get('key_points', 'Key points not provided')}")
                st.markdown("")
                question_num += 1
    else:
        st.error("❌ No exam data found")

def exam_generation():
    """Exam generation interface"""
    st.markdown("## 🎓 Generate Practice Exam")
    
    # Check if documents are uploaded
    if not st.session_state.uploaded_files:
        st.info("📥 Upload PDF documents first to generate exams from their content.")
        return
    
    st.markdown("Configure your practice exam settings:")
    
    # Create columns for exam configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Question Types & Counts:**")
        mcq_count = st.number_input("Multiple Choice", min_value=0, max_value=20, value=5)
        tf_count = st.number_input("True/False", min_value=0, max_value=20, value=5)
    
    with col2:
        st.markdown("**Additional Questions:**")
        sa_count = st.number_input("Short Answer", min_value=0, max_value=10, value=3)
        essay_count = st.number_input("Essay Questions", min_value=0, max_value=5, value=2)
    
    # Difficulty selection
    st.markdown("**Difficulty Level:**")
    difficulty = st.selectbox(
        "Choose difficulty level",
        ["easy", "medium", "hard", "expert"],
        index=1,  # Default to medium
        format_func=lambda x: {
            "easy": "🟢 Easy - Basic recall and definitions",
            "medium": "🟡 Medium - Application and understanding", 
            "hard": "🟠 Hard - Analysis and synthesis",
            "expert": "🔴 Expert - Critical thinking and mastery"
        }[x]
    )
    
    # Generate button
    if st.button("🚀 Generate Practice Exam", type="primary"):
        chatbot = get_or_create_chatbot()
        if not chatbot:
            return
        
        # Calculate total questions
        total_questions = mcq_count + tf_count + sa_count + essay_count
        
        if total_questions == 0:
            st.error("❌ Please select at least one question type with count > 0")
            return
        
        # Configure exam settings
        exam_config = {
            "multiple_choice": mcq_count,
            "true_false": tf_count,
            "short_answer": sa_count,
            "essay": essay_count,
            "difficulty": difficulty
        }
        
        with st.spinner(f"🎯 Generating {difficulty} difficulty exam with {total_questions} questions..."):
            result = chatbot.generate_exam(exam_config)
        
        if result["success"]:
            st.success(f"✅ Generated exam with {total_questions} questions!")
            
            # Store exam and answers in session state
            st.session_state.current_exam = result
            st.session_state.show_answers = False
            
    # Display exam if one exists
    if hasattr(st.session_state, 'current_exam') and st.session_state.current_exam:
        display_exam_with_answers(st.session_state.current_exam)
    
    # Handle case where exam generation failed
    if 'result' in locals() and not result["success"]:
        st.error(f"❌ Failed to generate exam: {result['error']}")

def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Check OpenAI setup
    if not check_openai_setup():
        return
    
    # Sidebar
    sidebar_controls()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📂 Upload Files", "💬 Chat", "🎓 Generate Exam"])
    
    with tab1:
        file_upload_section()
    
    with tab2:
        chat_interface()
    
    with tab3:
        exam_generation()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**AI Study Chatbot** | Powered by OpenAI GPT & RAG Technology | "
        "📚 Upload PDFs • 💬 Ask Questions • 🎓 Generate Exams"
    )

if __name__ == "__main__":
    main()