"""
AI-Powered Exam Generator
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
    
    def generate_multiple_choice(self, context: str, num_questions: int = 5) -> List[Dict]:
        """Generate multiple choice questions from context"""
        
        prompt = f"""Based on the following academic content, create {num_questions} multiple choice questions suitable for a study exam. 

Content:
{context[:4000]}  # Limit context to prevent token overflow

Instructions:
1. Create questions that test understanding of key concepts
2. Include 4 answer choices (A, B, C, D) for each question
3. Mark the correct answer
4. Make distractors plausible but clearly incorrect
5. Focus on important concepts, not trivial details

Format your response as a JSON array of objects with this structure:
{{
  "question": "The question text",
  "choices": {{
    "A": "First option",
    "B": "Second option", 
    "C": "Third option",
    "D": "Fourth option"
  }},
  "correct_answer": "A",
  "explanation": "Why this answer is correct"
}}

JSON Response:"""

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
            
            logger.info(f"Generated {len(questions)} multiple choice questions")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate multiple choice questions: {e}")
            return []
    
    def generate_true_false(self, context: str, num_questions: int = 5) -> List[Dict]:
        """Generate true/false questions from context"""
        
        prompt = f"""Based on the following academic content, create {num_questions} true/false questions.

Content:
{context[:4000]}

Instructions:
1. Create statements that test understanding of key concepts
2. Mix true and false statements evenly
3. Avoid overly obvious or tricky questions
4. Focus on important facts and concepts

Format as JSON array:
{{
  "statement": "The statement to evaluate",
  "correct_answer": true,
  "explanation": "Why this is true/false"
}}

JSON Response:"""

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
            
            logger.info(f"Generated {len(questions)} true/false questions")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate true/false questions: {e}")
            return []
    
    def generate_short_answer(self, context: str, num_questions: int = 3) -> List[Dict]:
        """Generate short answer questions from context"""
        
        prompt = f"""Based on the following academic content, create {num_questions} short answer questions.

Content:
{context[:4000]}

Instructions:
1. Create questions requiring 2-3 sentence answers
2. Focus on explaining concepts or processes
3. Include sample answers and key points
4. Test understanding, not memorization

Format as JSON array:
{{
  "question": "The question text",
  "sample_answer": "A good sample answer",
  "key_points": "Key concepts that should be mentioned"
}}

JSON Response:"""

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
            
            logger.info(f"Generated {len(questions)} short answer questions")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate short answer questions: {e}")
            return []
    
    def generate_essay_questions(self, context: str, num_questions: int = 2) -> List[Dict]:
        """Generate essay questions from context"""
        
        prompt = f"""Based on the following academic content, create {num_questions} essay questions.

Content:
{context[:4000]}

Instructions:
1. Create questions requiring detailed, analytical responses
2. Focus on synthesis, comparison, or critical thinking
3. Include key points that should be addressed
4. Provide sample essay outlines

Format as JSON array:
{{
  "question": "The essay question",
  "key_points": "Main points that should be addressed",
  "sample_outline": "A sample essay structure",
  "guidance": "Additional guidance for answering"
}}

JSON Response:"""

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
            
            logger.info(f"Generated {len(questions)} essay questions")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate essay questions: {e}")
            return []
    
    def generate_complete_exam(self, context: str, exam_config: Dict = None) -> Dict:
        """Generate a complete exam with multiple question types"""
        
        if exam_config is None:
            exam_config = {
                "multiple_choice": 5,
                "true_false": 5,
                "short_answer": 3,
                "essay": 2
            }
        
        exam = {
            "title": "AI-Generated Practice Exam",
            "instructions": "Answer all questions to the best of your ability. Use the material from your uploaded documents as reference.",
            "sections": {}
        }
        
        try:
            # Generate different question types
            if exam_config.get("multiple_choice", 0) > 0:
                mcq = self.generate_multiple_choice(context, exam_config["multiple_choice"])
                if mcq:
                    exam["sections"]["multiple_choice"] = {
                        "title": "Multiple Choice Questions",
                        "instructions": "Choose the best answer for each question.",
                        "questions": mcq
                    }
            
            if exam_config.get("true_false", 0) > 0:
                tf = self.generate_true_false(context, exam_config["true_false"])
                if tf:
                    exam["sections"]["true_false"] = {
                        "title": "True/False Questions",
                        "instructions": "Mark each statement as true or false.",
                        "questions": tf
                    }
            
            if exam_config.get("short_answer", 0) > 0:
                sa = self.generate_short_answer(context, exam_config["short_answer"])
                if sa:
                    exam["sections"]["short_answer"] = {
                        "title": "Short Answer Questions",
                        "instructions": "Provide concise answers in 2-3 sentences.",
                        "questions": sa
                    }
            
            if exam_config.get("essay", 0) > 0:
                essay = self.generate_essay_questions(context, exam_config["essay"])
                if essay:
                    exam["sections"]["essay"] = {
                        "title": "Essay Questions",
                        "instructions": "Provide detailed, well-structured answers.",
                        "questions": essay
                    }
            
            total_questions = sum(len(section["questions"]) for section in exam["sections"].values())
            exam["total_questions"] = total_questions
            
            logger.info(f"Generated complete exam with {total_questions} questions")
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
        output.append(f"\n**Instructions:** {exam.get('instructions', '')}")
        output.append(f"\n**Total Questions:** {exam.get('total_questions', 0)}")
        output.append("\n" + "="*50 + "\n")
        
        question_num = 1
        
        for section_key, section in exam.get("sections", {}).items():
            output.append(f"## {section.get('title', section_key.title())}")
            output.append(f"*{section.get('instructions', '')}*\n")
            
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
            
            output.append("\n" + "-"*30 + "\n")
        
        return "\n".join(output)
    
    def format_answers_for_display(self, exam: Dict) -> str:
        """Format exam with complete answer key for display"""
        
        if "error" in exam:
            return f"❌ Exam Generation Error: {exam['error']}"
        
        output = []
        output.append(f"# {exam.get('title', 'Practice Exam')} - Answer Key")
        output.append(f"\n**Complete Answer Key with Explanations**")
        output.append(f"**Total Questions:** {exam.get('total_questions', 0)}")
        output.append("\n" + "="*50 + "\n")
        
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
            
            output.append("\n" + "-"*30 + "\n")
        
        return "\n".join(output)

# Global exam generator instance
def get_exam_generator() -> ExamGenerator:
    """Get or create global exam generator instance"""
    if not hasattr(get_exam_generator, "_instance"):
        get_exam_generator._instance = ExamGenerator()
    return get_exam_generator._instance