import json
from groq import Groq
from typing import List, Dict
from tavily import TavilyClient
from models import Skill, SkillScore, LearningItem, LearningResource
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY)
tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

def find_score(skill_name: str, scores: Dict[str, SkillScore]):
    """Helper to find score in dict by name (case-insensitive)"""
    for name, score_obj in scores.items():
        if name.lower() == skill_name.lower():
            return score_obj
    return None

def get_gap_skills(skills: List[Skill], scores: Dict[str, SkillScore]):
    gap_skills = []
    
    for s in skills:
        score_obj = find_score(s.skill, scores)
        
        if score_obj is None:
            # No score recorded at all - include it
            gap_skills.append(s)
        elif score_obj.score <= 80:
            # Includes 0 scores explicitly
            gap_skills.append(s)
    
    # Always return at least something
    if not gap_skills and skills:
        # All scored very high - return lowest 2
        sorted_skills = sorted(
            skills,
            key=lambda s: find_score(s.skill, scores).score
                if find_score(s.skill, scores) else 0
        )
        gap_skills = sorted_skills[:2]
    
    print(f"Gap skills selected: {[(s.skill, find_score(s.skill, scores).score if find_score(s.skill, scores) else 'NO SCORE') for s in gap_skills]}")
    return gap_skills

async def generate_learning_plan(
    skills: List[Skill],
    scores: Dict[str, SkillScore],
    resume: str
) -> Dict:
    """
    Generate the entire learning plan in a single API call after gathering search results using Groq.
    """
    # Always generate a plan - split skills into tiers 
    gap_skills = get_gap_skills(skills, scores)
    
    if not gap_skills:
        return {"plan": [], "context": "none", "summary": "No assessment data found."}
    
    # Determine plan context based on weak skills
    weak_skills = [s for s in gap_skills if find_score(s.skill, scores) and find_score(s.skill, scores).score < 50]
    partial_skills = [s for s in gap_skills if find_score(s.skill, scores) and 50 <= find_score(s.skill, scores).score < 80]
    
    if not weak_skills and not partial_skills:
        plan_context = "senior_growth"  # focus on advanced/expert level resources
    elif weak_skills:
        plan_context = "foundational"   # focus on basics first
    else:
        plan_context = "intermediate"   # fill specific gaps
    
    # Calculate avg score for summary
    avg_score = sum(s.score for s in scores.values()) / len(scores) if scores else 0
    level_label = "Strong" if avg_score >= 80 else "Intermediate" if avg_score >= 50 else "Foundational"
    summary = f"{level_label} candidate (avg score {avg_score:.0f}%). Plan focuses on {'mastery areas' if plan_context == 'senior_growth' else 'specific gaps' if plan_context == 'intermediate' else 'foundational basics'}."
    
    # 1. Gather all search results first
    all_search_context = []
    for skill in gap_skills:
        score_data = find_score(skill.skill, scores)
        score_val = score_data.score if score_data else 0
        
        # Determine per-skill level context for Groq
        if score_val <= 0:
            level_context = "complete beginner with no prior knowledge. Generate a complete beginner roadmap starting from scratch."
        elif score_val < 50:
            level_context = "beginner with some exposure. Build on fundamentals toward job requirements."
        elif score_val < 75:
            level_context = "intermediate needing to fill specific gaps."
        else:
            level_context = "proficient candidate looking to reach expert level."

        search_query = f"{skill.skill} {'advanced architecture open source' if plan_context == 'senior_growth' else 'best courses 2025'} site:coursera.org OR site:udemy.com OR site:youtube.com"
        
        if settings.TAVILY_API_KEY.startswith("sk-0123456789"):
            search_result = {
                "results": [
                    {"title": f"Mastering {skill.skill} on Coursera", "url": "https://www.coursera.org/", "content": "..."}
                ]
            }
        else:
            try:
                search_result = tavily.search(query=search_query, search_depth="basic")
            except Exception:
                search_result = {"results": []}
        
        all_search_context.append({
            "skill": skill.skill,
            "score": score_val,
            "level_context": level_context,
            "gap": score_data.gap if score_data else "No specific gap identified.",
            "search_results": search_result['results'][:3]
        })

    # 2. Single call to Groq to generate the full plan
    system_prompt = """
    You are a personalized learning assistant. Create a comprehensive structured learning plan.
    
    PLAN CONTEXT: {{PLAN_CONTEXT}}
    - senior_growth: focus on advanced courses, architecture patterns, open source contribution.
    - intermediate: focus on specific gap-filling courses, hands-on projects.
    - foundational: focus on beginner courses, basics, projects, documentation.

    CANDIDATE CONTEXT:
    Resume: {{RESUME}}...
    
    SKILLS AND CONTEXT:
    {{GAPS_JSON}}
    
    GUIDELINES:
    - For EACH skill, review the "level_context" provided in the JSON.
    - If level_context indicates "complete beginner", start from absolute fundamentals.
    - If "beginner", build on basics.
    - If "intermediate", focus on specific advanced gaps.
    - Provide a 4-week breakdown and curate 2-3 resources for each skill.
    - Assume 1 hour of study per day.
    - Output a JSON object with a "plan" key containing a list of LearningItems.
    
    OUTPUT SCHEMA:
    {
        "plan": [
            {
                "skill": "string",
                "priority": 1,
                "time_weeks": 4,
                "why_adjacent": "string",
                "week_by_week": ["Week 1: ...", "Week 2: ...", "Week 3: ...", "Week 4: ..."],
                "resources": [
                    { "type": "course", "title": "string", "url": "string", "note": "string" }
                ]
            }
        ]
    }
    
    Only return the JSON object.
    """
    system_prompt = system_prompt.replace("{{PLAN_CONTEXT}}", plan_context)
    system_prompt = system_prompt.replace("{{RESUME}}", resume[:500])
    system_prompt = system_prompt.replace("{{GAPS_JSON}}", json.dumps(all_search_context))

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        plan_data = data.get("plan", []) if isinstance(data, dict) else data
        
        return {
            "plan": plan_data,
            "context": plan_context,
            "summary": summary
        }
    except Exception as e:
        print(f"Error generating full learning plan with Groq: {e}")
        return {"plan": [], "context": plan_context, "summary": summary}
