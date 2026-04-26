import json
from groq import Groq
from typing import List, Dict
from models import Skill, SkillScore
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

async def score_all_skills(
    skills: List[Skill],
    full_conversation_history: List[dict],
    response_metadata: List[dict] = None
) -> Dict[str, dict]:
    """
    Score all skills in a single batch call using Groq.
    Analyzes for AI-generated patterns and technical proficiency.
    """
    system_prompt = """
    You are a technical assessment engine. Evaluate the candidate's proficiency in multiple skills based on the provided interview conversation.
    
    SKILLS TO EVALUATE:
    {{SKILLS_JSON}}
    
    SCORING CRITERIA:
    - Score (0-100): 90-100 (Expert), 70-89 (Proficient), 40-69 (Intermediate), 0-39 (Beginner).
    - Confidence Signal: Detect from language:
        - genuine: specific versions, real project names, trade-offs mentioned.
        - hedging: uses I think, maybe, I believe, not sure, probably.
        - bluffing: sounds confident but zero specific details or examples.
    
    AI SUSPICION ANALYSIS:
    Analyze for AI-generated patterns:
    - Perfect grammar + zero personality (textbook style)
    - No first-person specific stories ("I built", "at my job we")
    - Buzzword dense but no concrete specifics
    
    Return:
    - ai_suspicion: "low", "medium", or "high"
    - suspicion_reason: A brief explanation (e.g., "No personal examples, textbook phrasing")
    
    OUTPUT FORMAT:
    Return a JSON object where keys are skill names and values are the score details.
    Example:
    {
        "React": {
            "score": 85,
            "level": "Proficient",
            "strength": "...",
            "gap": "...",
            "adjacent": true,
            "confidence_signal": "genuine",
            "ai_suspicion": "low",
            "suspicion_reason": ""
        }
    }
    
    Only return the JSON object.
    """
    system_prompt = system_prompt.replace("{{SKILLS_JSON}}", json.dumps([{'skill': s.skill, 'requirement': s.jd_requirement} for s in skills]))
    
    conv_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in full_conversation_history])
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CONVERSATION:\n{conv_str}"}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        scores_data = json.loads(content)
        
        # Post-process with response time metadata if available
        if response_metadata:
            for skill_name, score in scores_data.items():
                # Check if any answer for this skill was suspicious due to speed
                # For simplicity, we flag if ANY answer in the conversation was < 5s for complex content
                for meta in response_metadata:
                    res_time = meta.get("response_time")
                    if res_time is not None and res_time < 5 and len(meta.get("content", "")) > 150:
                        score["ai_suspicion"] = "high"
                        reason = "Suspiciously fast response time for complex answer."
                        score["suspicion_reason"] = f"{score.get('suspicion_reason', '')} {reason}".strip()
                        break
                        
        return scores_data
    except Exception as e:
        print(f"Error scoring skills batch with Groq: {e}")
        return {s.skill: {
            'score': 0, 
            'level': 'Beginner', 
            'strength': 'Error', 
            'gap': str(e), 
            'adjacent': False, 
            'confidence_signal': 'hedging',
            'ai_suspicion': 'low',
            'suspicion_reason': ''
        } for s in skills}

async def score_skill(
    skill: Skill,
    conversation: List[dict]
) -> SkillScore:
    """
    Legacy single-skill scorer using Groq.
    """
    system_prompt = """
    Evaluate the candidate's proficiency in "{{SKILL}}".
    JD Requirement: {{JD_REQ}}
    SCORING CRITERIA: 0-100 score, level, strength, gap, adjacent (bool).
    CONFIDENCE SIGNAL: Detect from the candidate's language:
        - genuine: specific versions, real project names, trade-offs mentioned.
        - hedging: uses I think, maybe, I believe, not sure, probably.
        - bluffing: sounds confident but zero specific details or examples.
      Return exactly one of: genuine, hedging, bluffing.
    Format: JSON object matching SkillScore schema.
    """
    system_prompt = system_prompt.replace("{{SKILL}}", skill.skill)
    system_prompt = system_prompt.replace("{{JD_REQ}}", skill.jd_requirement)
    
    conv_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in conversation])
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CONVERSATION:\n{conv_str}"}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        return SkillScore(**data)
    except Exception as e:
        print(f"Error scoring skill with Groq: {e}")
        return SkillScore(
            score=0, level="Beginner", strength="Error", gap=str(e), adjacent=False, confidence_signal="hedging"
        )

def get_score_signal(score: SkillScore) -> str:
    """Return "strong" if score >= 70, "weak" if score < 50, else "medium"."""
    if score.score >= 70:
        return "strong"
    if score.score < 50:
        return "weak"
    return "medium"
