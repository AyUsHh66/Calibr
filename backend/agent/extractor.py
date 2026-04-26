import json
from groq import Groq
from typing import List
from models import Skill
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

async def extract_skills(jd: str, resume: str) -> List[Skill]:
    """
    Call Groq (llama-3.3-70b-versatile) to extract 5-7 key skills from JD.
    """
    system_prompt = """
    You are an expert technical recruiter. Analyze the provided Job Description (JD) and Candidate Resume.
    
    1. Extract 5-7 key technical skills required by the JD.
    2. For each skill, determine its importance: "critical", "important", or "nice-to-have".
    3. Note the specific JD requirement for that skill.
    4. Format the output as a JSON object with a "skills" key containing an array of objects matching this schema:
    {
        "skills": [
            {
                "skill": "string",
                "importance": "critical" | "important" | "nice-to-have",
                "jd_requirement": "string"
            }
        ]
    }
    
    Only return the JSON object. Do not include any preamble, explanation, or markdown formatting blocks.
    """
    
    user_prompt = f"JOB DESCRIPTION:\n{jd}\n\nCANDIDATE RESUME:\n{resume}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    data = json.loads(content)
    # Groq with json_object might wrap the array in a key. Let's handle both.
    if isinstance(data, list):
        skills_data = data
    elif isinstance(data, dict) and "skills" in data:
        skills_data = data["skills"]
    elif isinstance(data, dict):
        # Try to find any list in the dict
        skills_data = next((v for v in data.values() if isinstance(v, list)), [])
    else:
        skills_data = []

    if not skills_data:
        raise ValueError(f"No skills found in Groq response: {content}")

    return [Skill(**item) for item in skills_data[:7]]
