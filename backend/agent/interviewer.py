import json
from groq import AsyncGroq
from typing import List, Optional
from models import Skill
from config import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

async def generate_questions_batch(
    skill: Skill,
    resume_context: str,
    num_questions: int = 2
) -> List[str]:
    """
    Generate all questions for a skill in a single API call using Groq.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "gsk_...":
        return [f"Tell me about your experience with {skill.skill}."] * num_questions

    system_prompt = """
    You are an expert technical interviewer assessing the skill: "{{SKILL}}".
    JD Requirement: {{JD_REQ}}
    Candidate Resume Context: {{RESUME}}
    
    TASK:
    Generate {{NUM_QS}} interview questions for this skill.
    
    GUIDELINES:
    1. Question 1 should be a practical, scenario-based opening question tailored to their resume.
    2. Question 2 should be a follow-up or a more advanced technical probe based on the expected knowledge level.
    3. Ensure questions are concise and professional.
    
    OUTPUT FORMAT:
    Return exactly {{NUM_QS}} questions as a JSON object with a "questions" key.
    Example: {"questions": ["Question 1", "Question 2"]}
    
    Only output the JSON object. No preamble or markdown.
    """
    system_prompt = system_prompt.replace("{{SKILL}}", skill.skill)
    system_prompt = system_prompt.replace("{{JD_REQ}}", skill.jd_requirement)
    system_prompt = system_prompt.replace("{{RESUME}}", resume_context)
    system_prompt = system_prompt.replace("{{NUM_QS}}", str(num_questions))
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Handle various JSON structures Groq might return
        if isinstance(data, list):
            questions = data
        elif isinstance(data, dict):
            questions = next((v for v in data.values() if isinstance(v, list)), [])
        else:
            questions = []

        if questions:
            return [str(q).strip() for q in questions]
        return [f"Tell me about your experience with {skill.skill}."] * num_questions
    except Exception as e:
        print(f"Error generating questions batch with Groq: {e}")
        return [f"Could you tell me more about your experience with {skill.skill}?"] * num_questions

async def generate_question(
    skill: Skill,
    resume_context: str,
    conversation_history: List[dict],
    question_number: int,
    last_score_signal: Optional[str] = None
) -> str:
    """
    Legacy single-question generator using Groq.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "gsk_...":
        return f"Tell me about your experience with {skill.skill}."

    system_prompt = """
    You are an expert technical interviewer assessing the skill: "{{SKILL}}".
    JD Requirement for this skill: {{JD_REQ}}
    Candidate Resume Context: {{RESUME}}
    
    Current Question Number: {{QN}}
    Last Performance Signal: {{SIGNAL}}
    
    GUIDELINES:
    1. If this is the FIRST question, ask a practical, scenario-based question.
    2. If the last answer was "strong", escalate difficulty.
    3. If the last answer was "weak", pivot to fundamentals.
    4. probed for specifics if they were vague.
    5. Keep questions concise.
    """
    system_prompt = system_prompt.replace("{{SKILL}}", skill.skill)
    system_prompt = system_prompt.replace("{{JD_REQ}}", skill.jd_requirement)
    system_prompt = system_prompt.replace("{{RESUME}}", resume_context)
    system_prompt = system_prompt.replace("{{QN}}", str(question_number))
    system_prompt = system_prompt.replace("{{SIGNAL}}", last_score_signal if last_score_signal else "N/A")
    
    history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation_history])
    prompt = f"{system_prompt}\n\nCONVERSATION HISTORY:\n{history_str}\n\nGenerate the next question:"
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating question with Groq: {e}")
        return f"Tell me about your experience with {skill.skill}."
