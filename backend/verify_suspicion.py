import asyncio
import json
from sqlmodel import Session, create_engine, select
from main import SessionModel, Skill, score_all_skills
from models import SkillScore

# Mock database for testing
sqlite_url = "sqlite:///./test.db"
engine = create_engine(sqlite_url)

async def test_suspicion_logic():
    print("Testing AI Suspicion Logic...")
    
    # 1. Test Data: Fast response for complex question
    skills = [Skill(skill="Python", importance="critical")]
    history = [
        {"role": "agent", "content": "Tell me about a complex Python project you built."},
        {"role": "user", "content": "I built a high-performance data processing pipeline using multiprocessing and asyncio. It handled millions of records per second with zero lag. The architecture was based on a producer-consumer pattern with distributed workers.", "response_time": 2.5}
    ]
    metadata = [
        {"content": history[1]["content"], "response_time": 2.5}
    ]
    
    print("\nScenario 1: Fast response (<5s) for long answer (>150 chars)")
    scores = await score_all_skills(skills, history, metadata)
    python_score = scores.get("Python", {})
    
    print(f"AI Suspicion: {python_score.get('ai_suspicion')}")
    print(f"Reason: {python_score.get('suspicion_reason')}")
    
    if python_score.get('ai_suspicion') == 'high' and "fast response" in python_score.get('suspicion_reason', '').lower():
        print("Γ£ô Success: Fast response correctly flagged.")
    else:
        print("Γ£û Failure: Fast response NOT correctly flagged.")

    # 2. Test Data: Pattern analysis (textbook style)
    print("\nScenario 2: Textbook style answer (pattern analysis)")
    history_textbook = [
        {"role": "agent", "content": "What are the benefits of React?"},
        {"role": "user", "content": "React is a declarative, efficient, and flexible JavaScript library for building user interfaces. It lets you compose complex UIs from small and isolated pieces of code called components. React has a component-based architecture and uses a virtual DOM for optimized rendering.", "response_time": 15.0}
    ]
    metadata_textbook = [
        {"content": history_textbook[1]["content"], "response_time": 15.0}
    ]
    
    # This relies on the actual LLM call in scorer.py
    scores_textbook = await score_all_skills(skills, history_textbook, metadata_textbook)
    python_score_textbook = scores_textbook.get("Python", {})
    
    print(f"AI Suspicion: {python_score_textbook.get('ai_suspicion')}")
    print(f"Reason: {python_score_textbook.get('suspicion_reason')}")

if __name__ == "__main__":
    asyncio.run(test_suspicion_logic())
