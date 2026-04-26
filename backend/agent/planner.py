import json
from groq import AsyncGroq
from typing import List, Dict
from tavily import TavilyClient
from models import Skill, SkillScore, LearningItem, LearningResource
from config import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)
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
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "gsk_...":
        return {"plan": [], "context": "none", "summary": "Groq API Key not configured. Plan generation skipped."}

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
            except:
                search_result = {"results": []}

        # Format context for Groq
        skill_context = f"SKILL: {skill.skill}\nGAP: {score_data.gap if score_data else 'New skill'}\nLEVEL: {level_context}\nWEB RESULTS:\n"
        for r in search_result.get("results", [])[:3]:
            skill_context += f"- {r['title']} ({r['url']}): {r['content'][:150]}...\n"
        
        all_search_context.append(skill_context)

    # 2. Final prompt for Groq to synthesize the plan
    system_prompt = f"""
    You are an AI Learning Mentor. Generate a personalized learning plan based on the candidate's assessment gaps.
    
    OVERALL PLAN CONTEXT: {plan_context}
    CANDIDATE RESUME SUMMARY: {resume[:500]}...
    
    OUTPUT FORMAT:
    Return a JSON object with a "plan" key containing a list of learning items.
    Return a JSON array. Each item MUST have these exact fields:
    {{
      "skill": string,
      "priority": number (1, 2, or 3),
      "time_weeks": number,
      "why_adjacent": string,
      "week_by_week": array of strings like ["Week 1: Do X", "Week 2: Do Y"],
      "resources": array of {{type, title, url, note}}
    }}
    
    The week_by_week field is REQUIRED. Always include at least 2 weekly milestones. Never omit it.
    Only return JSON. No preamble.
    """
    
    user_prompt = "GENERATE PLAN FROM THESE GAPS AND WEB RESOURCES:\n\n" + "\n---\n".join(all_search_context)
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        plan_data = json.loads(response.choices[0].message.content)
        plan = plan_data.get("plan", [])
        
        # Post-processing: ensure required fields exist
        for item in plan:
            if 'week_by_week' not in item or not item['week_by_week']:
                item['week_by_week'] = [
                    f"Week 1-2: Learn {item.get('skill', 'this skill')} fundamentals",
                    f"Week 3-4: Build a project using {item.get('skill', 'this skill')}",
                    f"Week 5+: Apply to real work scenarios"
                ]
            if 'resources' not in item or not item['resources']:
                item['resources'] = []
                
        return {
            "plan": plan,
            "context": plan_context,
            "summary": summary
        }
    except Exception as e:
        print(f"Error generating learning plan with Groq: {e}")
        return {"plan": [], "context": plan_context, "summary": f"Synthesis failed: {str(e)}"}
