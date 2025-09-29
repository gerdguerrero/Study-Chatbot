"""
AI-Powered Exam Generator with Difficulty Levels
Creates practice exams from uploaded documents using OpenAI
"""

import logging
from typing import List, Dict, Optional
import json
import openai
from config import settings, validate_openai_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExamGenerator:
    """Generates practice exams from document content using OpenAI"""
    
    def __init__(self):
        """Initialize exam generator"""
        if not validate_openai_key():
            raise ValueError("OpenAI API key required for exam generation")
        
        openai.api_key = settings.openai_api_key
        logger.info("Exam generator initialized")
    
    def generate_multiple_choice(self, context: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
        """Generate multiple choice questions from context with specified difficulty"""
        
        # Define difficulty-specific instructions
        difficulty_instructions = {
            "easy": "1. Focus on basic concepts, definitions, and direct facts\\n2. Use straightforward, clear language\\n3. Make correct answers obvious to someone who studied\\n4. Test recall and recognition",
            "medium": "1. Test understanding and application of concepts\\n2. Require some analysis and connection-making\\n3. Include scenarios that apply the knowledge\\n4. Balance recall with comprehension",
            "hard": "1. Require analysis, synthesis, and evaluation\\n2. Include complex scenarios and problem-solving\\n3. Test ability to distinguish between similar concepts\\n4. Require deep understanding of relationships",
            "expert": "1. Focus on critical thinking and expert-level analysis\\n2. Include edge cases and complex applications\\n3. Test mastery of nuanced distinctions\\n4. Require integration of multiple concepts"
        }
        
        difficulty_level = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])
        
        prompt = f"""Create {num_questions} multiple choice questions based ONLY on the technical content provided below.

IMPORTANT: Focus on the CORE TECHNICAL CONCEPTS, methods, procedures, and practical applications. 
AVOID questions about standards, regulations, organizations, or administrative topics unless they are central to the technical content.

Content:
{context[:3500]}

Difficulty Level: {difficulty.upper()}
{difficulty_level}

Each question must have:
- Question text based on technical content
- 4 answer choices (A, B, C, D)
- Correct answer marked
- Brief explanation

Respond with ONLY valid JSON array:
[
  {{
    "question": "Question about technical content",
    "choices": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation"
  }}
]"""

        try:
            response = openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating exam questions. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            
            logger.info(f"Generated {len(questions)} multiple choice questions at {difficulty} difficulty")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate multiple choice questions: {e}")
            return []
    
    def generate_true_false(self, context: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
        """Generate true/false questions from context with specified difficulty"""
        
        difficulty_instructions = {
            "easy": "Create straightforward statements about basic facts and definitions",
            "medium": "Create statements that require understanding of concepts and their applications", 
            "hard": "Create statements that require analysis of relationships and complex reasoning",
            "expert": "Create statements that test mastery of nuanced distinctions and expert knowledge"
        }
        
        difficulty_level = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])
        
        prompt = f"""Create {num_questions} true/false questions based ONLY on the technical content provided below.

IMPORTANT: Focus on the CORE TECHNICAL CONCEPTS, methods, procedures, and practical applications.
AVOID questions about standards, regulations, organizations, or administrative topics unless they are central to the technical content.

Content:
{context[:3500]}

Difficulty Level: {difficulty.upper()}
{difficulty_level}

Create statements that can be verified from the technical content provided.
Mix true and false statements evenly.

Respond with ONLY valid JSON array:
[
  {{
    "statement": "Statement about technical content",
    "correct_answer": true,
    "explanation": "Brief explanation"
  }}
]"""

        try:
            response = openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating exam questions. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            
            logger.info(f"Generated {len(questions)} true/false questions at {difficulty} difficulty")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate true/false questions: {e}")
            return []
    
    def generate_short_answer(self, context: str, num_questions: int = 3, difficulty: str = "medium") -> List[Dict]:
        """Generate short answer questions from context with specified difficulty"""
        
        difficulty_instructions = {
            "easy": "Create questions asking for basic definitions, simple explanations, or direct facts (1-2 sentences)",
            "medium": "Create questions requiring explanation of concepts, processes, or applications (2-3 sentences)",
            "hard": "Create questions requiring analysis, comparison, or synthesis of multiple concepts (3-4 sentences)", 
            "expert": "Create questions requiring critical evaluation, complex reasoning, or expert insights (4-5 sentences)"
        }
        
        difficulty_level = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])
        
        prompt = f"""Create {num_questions} short answer questions based ONLY on the technical content provided below.

IMPORTANT: Focus on the CORE TECHNICAL CONCEPTS, methods, procedures, and practical applications.
AVOID questions about standards, regulations, organizations, or administrative topics unless they are central to the technical content.

Content:
{context[:3500]}

Difficulty Level: {difficulty.upper()}
{difficulty_level}

Respond with ONLY valid JSON array:
[
  {{
    "question": "Question about technical content",
    "answer": "Sample answer based on content",
    "key_points": "Key technical points to mention"
  }}
]"""

        try:
            response = openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating exam questions. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            
            logger.info(f"Generated {len(questions)} short answer questions at {difficulty} difficulty")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate short answer questions: {e}")
            return []
    
    def generate_essay_questions(self, context: str, num_questions: int = 2, difficulty: str = "medium") -> List[Dict]:
        """Generate essay questions from context with specified difficulty"""
        
        difficulty_instructions = {
            "easy": "Create questions asking for basic explanations or descriptions of concepts",
            "medium": "Create questions requiring detailed analysis, comparison, or application of concepts",
            "hard": "Create questions requiring synthesis, evaluation, or complex problem-solving",
            "expert": "Create questions requiring critical analysis, original thinking, or expert-level evaluation"
        }
        
        difficulty_level = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])
        
        prompt = f"""Create {num_questions} essay questions based ONLY on the technical content provided below.

IMPORTANT: Focus on the CORE TECHNICAL CONCEPTS, methods, procedures, and practical applications.
AVOID questions about standards, regulations, organizations, or administrative topics unless they are central to the technical content.

Content:
{context[:3500]}

Difficulty Level: {difficulty.upper()}
{difficulty_level}

Respond with ONLY valid JSON array:
[
  {{
    "question": "Essay question about technical content",
    "key_points": "Main technical points to address",
    "guidance": "Guidance for answering"
  }}
]"""

        try:
            response = openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating exam questions. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            questions = json.loads(content)
            
            logger.info(f"Generated {len(questions)} essay questions at {difficulty} difficulty")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate essay questions: {e}")
            return []
    
    def generate_complete_exam(self, context: str, exam_config: Dict = None) -> Dict:
        """Generate a complete exam with multiple question types and difficulty level"""
        
        if exam_config is None:
            exam_config = {
                "multiple_choice": 5,
                "true_false": 5,
                "short_answer": 3,
                "essay": 2,
                "difficulty": "medium"
            }
        
        # Extract difficulty level from config
        difficulty = exam_config.get("difficulty", "medium")
        
        exam = {
            "title": f"AI-Generated Practice Exam ({difficulty.title()} Difficulty)",
            "instructions": f"Answer all questions to the best of your ability. This exam is set to {difficulty.upper()} difficulty level.",
            "sections": {}
        }
        
        try:
            # Generate different question types with difficulty
            if exam_config.get("multiple_choice", 0) > 0:
                mcq = self.generate_multiple_choice(context, exam_config["multiple_choice"], difficulty)
                if mcq:
                    exam["sections"]["multiple_choice"] = {
                        "title": "Multiple Choice Questions",
                        "instructions": "Choose the best answer for each question.",
                        "questions": mcq
                    }
            
            if exam_config.get("true_false", 0) > 0:
                tf = self.generate_true_false(context, exam_config["true_false"], difficulty)
                if tf:
                    exam["sections"]["true_false"] = {
                        "title": "True/False Questions",
                        "instructions": "Mark each statement as true or false.",
                        "questions": tf
                    }
            
            if exam_config.get("short_answer", 0) > 0:
                sa = self.generate_short_answer(context, exam_config["short_answer"], difficulty)
                if sa:
                    exam["sections"]["short_answer"] = {
                        "title": "Short Answer Questions",
                        "instructions": "Provide concise answers in 2-3 sentences.",
                        "questions": sa
                    }
            
            if exam_config.get("essay", 0) > 0:
                essay = self.generate_essay_questions(context, exam_config["essay"], difficulty)
                if essay:
                    exam["sections"]["essay"] = {
                        "title": "Essay Questions",
                        "instructions": "Provide detailed, well-structured answers.",
                        "questions": essay
                    }
            
            total_questions = sum(len(section["questions"]) for section in exam["sections"].values())
            exam["total_questions"] = total_questions
            
            logger.info(f"Generated complete {difficulty} difficulty exam with {total_questions} questions")
            return exam
            
        except Exception as e:
            logger.error(f"Failed to generate complete exam: {e}")
            return {
                "title": "Exam Generation Failed",
                "error": str(e),
                "sections": {}
            }
    
    def format_exam_for_display(self, exam: Dict) -> str:
        """Format exam for display in the UI (questions only)"""
        
        if "error" in exam:
            return f"❌ Exam Generation Error: {exam['error']}"
        
        output = []
        output.append(f"# {exam.get('title', 'Practice Exam')}")
        output.append(f"\\n**Instructions:** {exam.get('instructions', '')}")
        output.append(f"\\n**Total Questions:** {exam.get('total_questions', 0)}")
        output.append("\\n" + "="*50 + "\\n")
        
        question_num = 1
        
        for section_key, section in exam.get("sections", {}).items():
            output.append(f"## {section.get('title', section_key.title())}")
            output.append(f"*{section.get('instructions', '')}*\\n")
            
            for q in section.get("questions", []):
                if section_key == "multiple_choice":
                    output.append(f"**Question {question_num}:** {q.get('question', '')}")
                    for choice, text in q.get("choices", {}).items():
                        output.append(f"  {choice}) {text}")
                    output.append("")  # Blank line
                
                elif section_key == "true_false":
                    output.append(f"**Question {question_num}:** {q.get('statement', '')} (True/False)")
                    output.append("")
                
                elif section_key == "short_answer":
                    output.append(f"**Question {question_num}:** {q.get('question', '')}")
                    output.append("_____________________")
                    output.append("")
                
                elif section_key == "essay":
                    output.append(f"**Question {question_num}:** {q.get('question', '')}")
                    if q.get('guidance'):
                        output.append(f"*Guidance: {q.get('guidance', '')}*")
                    output.append("")
                
                question_num += 1
            
            output.append("\\n" + "-"*30 + "\\n")
        
        return "\\n".join(output)
    
    def format_answers_for_display(self, exam: Dict) -> str:
        """Format exam with complete answer key for display"""
        
        if "error" in exam:
            return f"❌ Exam Generation Error: {exam['error']}"
        
        output = []
        output.append(f"# {exam.get('title', 'Practice Exam')} - Answer Key")
        output.append(f"\\n**Complete Answer Key with Explanations**")
        output.append(f"**Total Questions:** {exam.get('total_questions', 0)}")
        output.append("\\n" + "="*50 + "\\n")
        
        question_num = 1
        
        for section_key, section in exam.get("sections", {}).items():
            output.append(f"## {section.get('title', section_key.title())} - Answers")
            
            for q in section.get("questions", []):
                if section_key == "multiple_choice":
                    output.append(f"**Question {question_num}:** {q.get('question', '')}")
                    for choice, text in q.get("choices", {}).items():
                        if choice == q.get('correct_answer'):
                            output.append(f"  ✅ **{choice}) {text}** ← CORRECT ANSWER")
                        else:
                            output.append(f"  {choice}) {text}")
                    if q.get('explanation'):
                        output.append(f"💡 **Explanation:** {q.get('explanation', '')}")
                    output.append("")
                
                elif section_key == "true_false":
                    output.append(f"**Question {question_num}:** {q.get('statement', '')} (True/False)")
                    correct = "True" if q.get('correct_answer', False) else "False"
                    output.append(f"✅ **Correct Answer:** {correct}")
                    if q.get('explanation'):
                        output.append(f"💡 **Explanation:** {q.get('explanation', '')}")
                    output.append("")
                
                elif section_key == "short_answer":
                    output.append(f"**Question {question_num}:** {q.get('question', '')}")
                    if q.get('sample_answer'):
                        output.append(f"📝 **Sample Answer:** {q.get('sample_answer', '')}")
                    if q.get('key_points'):
                        output.append(f"🔑 **Key Points:** {q.get('key_points', '')}")
                    output.append("")
                
                elif section_key == "essay":
                    output.append(f"**Question {question_num}:** {q.get('question', '')}")
                    if q.get('key_points'):
                        output.append(f"📋 **Key Points to Address:** {q.get('key_points', '')}")
                    if q.get('sample_outline'):
                        output.append(f"📖 **Sample Essay Outline:** {q.get('sample_outline', '')}")
                    if q.get('guidance'):
                        output.append(f"💭 **Additional Guidance:** {q.get('guidance', '')}")
                    output.append("")
                
                question_num += 1
            
            output.append("\\n" + "-"*30 + "\\n")
        
        return "\\n".join(output)

# Global exam generator instance
def get_exam_generator() -> ExamGenerator:
    """Get or create global exam generator instance"""
    if not hasattr(get_exam_generator, "_instance"):
        get_exam_generator._instance = ExamGenerator()
    return get_exam_generator._instance