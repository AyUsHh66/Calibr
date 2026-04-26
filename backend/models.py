from datetime import datetime
from typing import Literal, List, Optional
from uuid import uuid4
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class Skill(BaseModel):
    skill: str
    importance: Literal["critical", "important", "nice-to-have"]
    jd_requirement: str

class SkillScore(BaseModel):
    score: int  # 0-100
    level: Literal["Beginner", "Intermediate", "Proficient", "Expert"]
    strength: str
    gap: str
    adjacent: bool  # can realistically upskill in <3 months
    confidence_signal: str  # "genuine" | "hedging" | "bluffing"
    ai_suspicion: Literal["low", "medium", "high"] = "low"
    suspicion_reason: str = ""

class Session(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    jd: str
    resume: str
    skills: str  # JSON string
    scores: Optional[str] = None  # JSON string
    status: str = "assessing"  # "assessing" | "complete"
    current_skill_index: int = 0
    current_question_number: int = 1
    questions_cache: Optional[str] = None  # JSON string: {skill_name: [q1, q2, ...]}
    chat_history: Optional[str] = None  # JSON string: [{"role": "user/assistant", "content": "..."}]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LearningResource(BaseModel):
    type: Literal["course", "book", "project", "doc"]
    title: str
    url: str
    note: str

class LearningItem(BaseModel):
    skill: str
    priority: int
    time_weeks: int
    why_adjacent: str
    week_by_week: List[str]  # ["Week 1: ...", "Week 2: ..."]
    resources: List[LearningResource]
