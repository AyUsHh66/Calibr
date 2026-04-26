import json
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from utils.pdf_extractor import extract_text_from_pdf
import io
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from db import engine, get_session, create_db_and_tables
from models import Session as SessionModel, Skill, SkillScore
from config import settings
from agent.extractor import extract_skills
from agent.interviewer import generate_question, generate_questions_batch
from agent.scorer import score_skill, get_score_signal, score_all_skills
from agent.planner import generate_learning_plan
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import StreamingResponse, Response
import asyncio
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO

from fastapi import Request
import time

app = FastAPI(
    title="Calibr API",
    description="AI-powered skill assessment and learning roadmap generator",
)

# 1. Explicit CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://calibr-zeta.vercel.app", "http://localhost:5174", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 2. Add OPTIONS handler for preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {"status": "ok"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
async def root():
    return {
        "message": "Calibr API is running",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api")
async def api_root():
    return {
        "message": "Calibr API v1",
        "health": "/api/health",
        "endpoints": [
            "/api/sessions",
            "/api/upload",
            "/api/recruiter/candidates"
        ]
    }

@app.get("/api/health")
@app.get("/health")
async def health_check():
    import os
    import time
    db_file_exists = False
    if "sqlite" in settings.DATABASE_URL:
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_file_exists = os.path.exists(db_path)
    
    return {
        "status": "healthy",
        "version": "1.0.1-pdf-debug",
        "time": time.time(),
        "database": settings.DATABASE_URL.split(":")[0],
        "db_file_exists": db_file_exists,
        "groq_configured": settings.GROQ_API_KEY != "gsk_...",
        "cors_origins": ["*"]
    }

@app.on_event("startup")
def on_startup():
    try:
        print("Starting up: Creating database tables...")
        create_db_and_tables()
        print("Database tables ensured.")
    except Exception as e:
        print(f"Startup error: Failed to create database tables: {e}")
        # We don't raise here to allow the app to start and show health check errors instead

class SessionRequest(BaseModel):
    jd: str
    resume: str

@app.post("/api/upload") 
async def upload_file(file: UploadFile = File(...)): 
    """Handle PDF and TXT file uploads, return extracted text.""" 
    try: 
        content = await file.read() 
        
        filename = file.filename.lower() 
        
        if filename.endswith(".pdf"): 
            text = extract_text_from_pdf(content) 
            
        elif filename.endswith(".txt"): 
            text = content.decode("utf-8", errors="ignore") 
            
        elif filename.endswith(".docx"): 
            # Handle docx with python-docx 
            import docx 
            import io 
            doc = docx.Document(io.BytesIO(content)) 
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()]) 
            
        else: 
            raise ValueError("Unsupported file type. Please upload PDF, TXT, or DOCX.") 
        
        if len(text.strip()) < 50: 
            raise ValueError("File appears empty or has too little text to analyse.") 
            
        return { 
            "success": True, 
            "text": text, 
            "filename": file.filename, 
            "char_count": len(text) 
        } 
        
    except ValueError as e: 
        return {"success": False, "error": str(e)} 
    except Exception as e: 
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

@app.post("/api/sessions")
async def create_session(data: SessionRequest, db: Session = Depends(get_session)):
    """
    Creates a new assessment session, extracts skills from JD and Resume.
    """
    print(f"Received create_session request. JD length: {len(data.jd)}, Resume length: {len(data.resume)}")
    try:
        # 1. Extract skills using Groq
        print("Starting skill extraction...")
        skills = await extract_skills(data.jd, data.resume)
        print(f"Successfully extracted {len(skills)} skills")
            
        # 2. Create session in DB
        print("Creating session record in database...")
        new_session = SessionModel(
            jd=data.jd,
            resume=data.resume,
            skills=json.dumps([s.model_dump() for s in skills]),
            status="assessing"
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        print(f"Session created with ID: {new_session.id}")
        
        return {
            "session_id": new_session.id,
            "skills": skills
        }
    except ValueError as ve:
        print(f"Validation error in create_session: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Critical error in create_session: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session_details(session_id: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "status": session.status,
        "current_skill_index": session.current_skill_index,
        "current_question_number": session.current_question_number,
        "skills": json.loads(session.skills),
        "scores": json.loads(session.scores) if session.scores else {},
        "chat_history": json.loads(session.chat_history) if session.chat_history else [],
        "created_at": session.created_at
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}

@app.get("/api/sessions/{session_id}/question")
async def get_question(
    session_id: str, 
    skill_index: int, 
    question_number: int,
    db: Session = Depends(get_session)
):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    skills_data = json.loads(session.skills)
    if skill_index >= len(skills_data):
        raise HTTPException(status_code=400, detail="Invalid skill index")
    
    skill = Skill(**skills_data[skill_index])
    
    # Check if we have cached questions for this skill
    cache = json.loads(session.questions_cache) if session.questions_cache else {}
    skill_questions = cache.get(skill.skill, [])
    
    if not skill_questions:
        # Generate all questions for this skill upfront
        skill_questions = await generate_questions_batch(
            skill=skill,
            resume_context=session.resume,
            num_questions=2
        )
        # Update cache in DB
        cache[skill.skill] = skill_questions
        session.questions_cache = json.dumps(cache)
        db.add(session)
        db.commit()
    
    # Return the requested question from cache
    if question_number <= len(skill_questions):
        question = skill_questions[question_number - 1]
        
        # Sync assistant question to chat_history if it's not already there
        current_history = json.loads(session.chat_history) if session.chat_history else []
        # Simple check to avoid duplicate assistant messages in history if refreshed
        if not current_history or current_history[-1].get("content") != question:
            current_history.append({"role": "assistant", "content": question, "skill": skill.skill})
            session.chat_history = json.dumps(current_history)
            db.add(session)
            db.commit()
            
        return {"question": question}
    
    return {"question": f"Could you tell me more about your experience with {skill.skill}?"}

class AnswerSubmit(BaseModel):
    skill_index: int
    question_number: int
    answer: str
    conversation_history: List[dict] # Frontend tracks the current skill's conversation
    response_time: Optional[float] = None

@app.post("/api/sessions/{session_id}/answer")
async def submit_answer(
    session_id: str,
    data: AnswerSubmit,
    db: Session = Depends(get_session)
):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    skills_data = json.loads(session.skills)
    skill = Skill(**skills_data[data.skill_index])
    
    # Update chat history with metadata
    user_msg = {"role": "user", "content": data.answer, "skill": skill.skill}
    if data.response_time is not None:
        user_msg["response_time"] = data.response_time

    full_history = data.conversation_history + [user_msg]
    session.chat_history = json.dumps(full_history)
    
    # If this is the last question for this skill (assuming 2 per skill as per spec)
    if data.question_number >= 2:
        # Check if all skills are done
        if data.skill_index >= len(skills_data) - 1:
            # ALL SKILLS DONE - Batch Score Everything Now
            session.status = "complete"
            
            all_skills = [Skill(**s) for s in skills_data]
            # Extract metadata for scoring
            response_metadata = [
                {"content": m["content"], "response_time": m.get("response_time")} 
                for m in full_history if m["role"] == "user"
            ]
            
            all_scores = await score_all_skills(all_skills, full_history, response_metadata)
            
            session.scores = json.dumps(all_scores)
            next_action = "complete"
            score_to_return = all_scores.get(skill.skill)
        else:
            # Just move to next skill, scoring happens at the very end
            next_action = "next_skill"
            session.current_skill_index = data.skill_index + 1
            session.current_question_number = 1
            score_to_return = None
            
        db.add(session)
        db.commit()
        
        return {
            "next_action": next_action,
            "score": score_to_return
        }
    
    session.current_question_number = data.question_number + 1
    db.add(session)
    db.commit()
    return {"next_action": "next_question"}

@app.get("/api/sessions/{session_id}/analysis")
async def get_analysis(session_id: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.scores:
        return {"error": "Assessment not complete"}
    
    scores = json.loads(session.scores)
    skills = [Skill(**s) for s in json.loads(session.skills)]
    
    # 1. Calculate JD Match Score (Weighted Average)
    weights = {"critical": 3, "important": 2, "nice-to-have": 1}
    total_weighted_score = 0
    total_weight = 0
    
    for skill_obj in skills:
        skill_name = skill_obj.skill
        weight = weights.get(skill_obj.importance, 1)
        score_val = scores.get(skill_name, {}).get("score", 0)
        
        total_weighted_score += score_val * weight
        total_weight += weight
    
    jd_match_score = int(total_weighted_score / total_weight) if total_weight > 0 else 0
    
    # 2. Determine Candidate Level
    avg_score = sum(s.get("score", 0) for s in scores.values()) / len(scores) if scores else 0
    if avg_score < 40:
        candidate_level = "Junior"
    elif avg_score < 60:
        candidate_level = "Mid-level"
    elif avg_score < 80:
        candidate_level = "Senior"
    else:
        candidate_level = "Expert"
        
    # 3. Get AI Verdict from Groq
    from agent.scorer import client as groq_client
    
    prompt = f"""
    Based on the following skill assessment results for a candidate, provide a one-sentence AI verdict.
    The verdict should be concise and mention key strengths or critical gaps relative to the role.
    
    JD Match Score: {jd_match_score}%
    Candidate Level: {candidate_level}
    Skill Scores: {json.dumps(scores)}
    
    Example verdict: "Strong frontend profile but critical DevOps gaps suggest mid-level fit over the senior role advertised."
    """
    
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        ai_verdict = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting AI verdict: {e}")
        ai_verdict = f"Candidate shows {candidate_level} proficiency with a {jd_match_score}% overall JD match."

    return {
        "scores": scores,
        "jd_match_score": jd_match_score,
        "ai_verdict": ai_verdict,
        "candidate_level": candidate_level
    }

@app.get("/api/recruiter/candidates")
async def get_recruiter_candidates(db: Session = Depends(get_session)):
    """
    Returns a list of all candidates who have completed their assessment.
    """
    try:
        statement = select(SessionModel).where(SessionModel.status == "complete")
        results = db.exec(statement).all()
        
        candidates = []
        for session in results:
            # Parse candidate name (first line of resume)
            resume_lines = session.resume.strip().split('\n')
            candidate_name = resume_lines[0] if resume_lines else "Unknown Candidate"
            
            scores = json.loads(session.scores) if session.scores else {}
            skills = [Skill(**s) for s in json.loads(session.skills)]
            
            # Calculate scores and metrics
            weights = {"critical": 3, "important": 2, "nice-to-have": 1}
            total_weighted_score = 0
            total_weight = 0
            overall_score_sum = 0
            
            # Top Gap: lowest scoring critical skill
            critical_skills_scores = []
            
            # Confidence avg: most common confidence signal
            confidence_signals = []
            ai_suspicions = []
            
            skills_summary = []
            
            for skill_obj in skills:
                skill_name = skill_obj.skill
                weight = weights.get(skill_obj.importance, 1)
                score_data = scores.get(skill_name, {})
                score_val = score_data.get("score", 0)
                conf_signal = score_data.get("confidence_signal", "genuine")
                ai_suspicion = score_data.get("ai_suspicion", "low")
                
                total_weighted_score += score_val * weight
                total_weight += weight
                overall_score_sum += score_val
                
                if skill_obj.importance == "critical":
                    critical_skills_scores.append((skill_name, score_val))
                
                confidence_signals.append(conf_signal)
                ai_suspicions.append(ai_suspicion)
                skills_summary.append({
                    "skill": skill_name,
                    "score": score_val,
                    "confidence_signal": conf_signal,
                    "ai_suspicion": ai_suspicion
                })
                
            # Calculate overall suspicion
            if "high" in ai_suspicions:
                overall_suspicion = "high"
            elif "medium" in ai_suspicions:
                overall_suspicion = "medium"
            else:
                overall_suspicion = "low"

            jd_match_score = int(total_weighted_score / total_weight) if total_weight > 0 else 0
            overall_score = int(overall_score_sum / len(skills)) if skills else 0
            
            # Find top gap
            top_gap = "None"
            if critical_skills_scores:
                critical_skills_scores.sort(key=lambda x: x[1])
                top_gap = critical_skills_scores[0][0]
                
            # Find most common confidence signal
            from collections import Counter
            conf_counts = Counter(confidence_signals)
            confidence_avg = conf_counts.most_common(1)[0][0] if confidence_signals else "genuine"
            
            candidates.append({
                "session_id": session.id,
                "candidate_name": candidate_name,
                "overall_score": overall_score,
                "jd_match_score": jd_match_score,
                "top_gap": top_gap,
                "confidence_avg": confidence_avg,
                "ai_suspicion": overall_suspicion,
                "assessed_at": session.created_at.isoformat(),
                "skills_summary": skills_summary
            })
            
        # Sort by JD match score descending by default
        candidates.sort(key=lambda x: x["jd_match_score"], reverse=True)
        
        return candidates
    except Exception as e:
        print(f"Recruiter endpoint error: {e}")
        return []

@app.get("/api/recruiter/compare")
async def compare_candidates(session_ids: str, db: Session = Depends(get_session)):
    """
    Compares multiple candidates side-by-side.
    """
    ids = session_ids.split(",")
    results = []
    
    all_skills_set = set()
    
    for sid in ids:
        session = db.get(SessionModel, sid)
        if not session:
            continue
            
        resume_lines = session.resume.strip().split('\n')
        candidate_name = resume_lines[0] if resume_lines else "Unknown Candidate"
        
        scores = json.loads(session.scores) if session.scores else {}
        skills_data = json.loads(session.skills)
        
        # Get overall metrics from previous logic
        # For simplicity, we'll re-calculate or fetch from session if we stored them
        # Let's re-calculate to be safe
        weights = {"critical": 3, "important": 2, "nice-to-have": 1}
        total_weighted_score = 0
        total_weight = 0
        confidence_signals = []
        ai_suspicions = []
        
        candidate_skills = {}
        for s in skills_data:
            skill_name = s['skill']
            all_skills_set.add(skill_name)
            
            score_data = scores.get(skill_name, {})
            score_val = score_data.get("score", 0)
            conf_signal = score_data.get("confidence_signal", "genuine")
            ai_suspicion = score_data.get("ai_suspicion", "low")
            
            weight = weights.get(s['importance'], 1)
            total_weighted_score += score_val * weight
            total_weight += weight
            confidence_signals.append(conf_signal)
            ai_suspicions.append(ai_suspicion)
            
            candidate_skills[skill_name] = {
                "score": score_val,
                "level": score_data.get("level", "Beginner")
            }
            
        jd_match_score = int(total_weighted_score / total_weight) if total_weight > 0 else 0
        
        from collections import Counter
        conf_avg = Counter(confidence_signals).most_common(1)[0][0] if confidence_signals else "genuine"
        
        if "high" in ai_suspicions:
            suspicion_avg = "high"
        elif "medium" in ai_suspicions:
            suspicion_avg = "medium"
        else:
            suspicion_avg = "low"
            
        results.append({
            "session_id": sid,
            "name": candidate_name,
            "jd_match": jd_match_score,
            "confidence": conf_avg,
            "ai_suspicion": suspicion_avg,
            "skills": candidate_skills
        })
        
    if len(results) < 2:
        return {"error": "Need at least 2 candidates to compare"}
        
    # Generate AI Comparison Verdict
    comparison_context = json.dumps(results)
    prompt = f"""
    Compare these candidates for the role. Provide a ONE-LINE verdict explaining who is stronger and why.
    Candidates: {comparison_context}
    
    Example: "Jane is stronger due to higher proficiency in critical React and Node.js skills, despite Alex's lower AI suspicion."
    """
    
    from agent.scorer import client as groq_client
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        verdict = response.choices[0].message.content.strip()
    except Exception as e:
        verdict = f"Comparison complete: {results[0]['name']} and {results[1]['name']} evaluated."

    return {
        "candidates": results,
        "all_skills": sorted(list(all_skills_set)),
        "verdict": verdict
    }
@app.get("/api/sessions/{session_id}/plan")
async def get_learning_plan(session_id: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def event_generator():
        # Yield a heartbeat or initial status to keep connection alive
        yield f"data: {json.dumps({'type': 'status', 'message': 'Generating your personalized roadmap...'})}\n\n"
        
        try:
            skills = [Skill(**s) for s in json.loads(session.skills)]
            scores = {k: SkillScore(**v) for k, v in json.loads(session.scores).items()}
            
            result = await generate_learning_plan(skills, scores, session.resume)
            
            # Send context and summary
            yield f"data: {json.dumps({'type': 'metadata', 'context': result['context'], 'summary': result['summary']})}\n\n"
            
            for item in result['plan']:
                yield f"data: {json.dumps({'type': 'item', 'data': item})}\n\n"
                await asyncio.sleep(0.1)
            
            yield "data: {\"type\": \"done\"}\n\n"
        except Exception as e:
            print(f"SSE Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

def generate_pdf(session) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#7c6bff'),
        spaceAfter=12)
    story.append(Paragraph("Calibr — Skill Assessment Report", title_style))
    story.append(Spacer(1, 12))
    
    # Session info
    story.append(Paragraph(f"Session ID: {session.id[:8]}...", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Skills and scores
    scores = {}
    try:
        scores = json.loads(session.scores) if session.scores else {}
    except:
        scores = {}
    
    skills = []
    try:
        skills = json.loads(session.skills) if session.skills else []
    except:
        skills = []
    
    if skills:
        story.append(Paragraph("Skill Assessment Results", styles['Heading1']))
        story.append(Spacer(1, 8))
        
        # Table data
        table_data = [['Skill', 'Score', 'Level', 'Confidence']]
        for skill in skills:
            # Skill can be a dict or a Skill object depending on how it's loaded
            skill_name = skill.get('skill', 'Unknown') if isinstance(skill, dict) else getattr(skill, 'skill', 'Unknown')
            
            score_data = scores.get(skill_name, {})
            score = score_data.get('score', 'N/A')
            level = score_data.get('level', 'N/A')
            confidence = score_data.get('confidence_signal', 'N/A')
            table_data.append([skill_name, str(score), level, confidence])
        
        table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#7c6bff')),
            ('TEXTCOLOR', (0,0), (-1,0), HexColor('#ffffff')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [HexColor('#f8f8ff'), HexColor('#ffffff')]),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#dddddd')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Generated by Calibr — AI Skill Assessment Agent",
        styles['Normal']
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

@app.get("/api/sessions/{session_id}/plan/pdf")
async def get_plan_pdf(session_id: str, db: Session = Depends(get_session)):
    try:
        print(f"PDF requested for session: {session_id}")
        
        session = db.get(SessionModel, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        print(f"Session found, generating PDF...")
        pdf_bytes = generate_pdf(session)
        print(f"PDF generated: {len(pdf_bytes)} bytes")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=calibr-report-{session_id[:8]}.pdf",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"PDF ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        # Return error with CORS headers so browser can read it
        return Response(
            content=str(e),
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

# Catch-all for undefined /api routes to help debug 404s
# @app.api_route("/api/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
# async def catch_all_api(request: Request, path_name: str):
#     print(f"DEBUG: 404 Attempted access to undefined route: {request.method} {request.url.path}")
#     return Response(
#         content=json.dumps({"detail": f"Route {request.url.path} not found on this server"}),
#         status_code=404,
#         media_type="application/json"
#     )

class LearningResource(BaseModel):
    title: str
    url: str
    type: str

class LearningItem(BaseModel):
    skill: str
    priority: int
    time_weeks: int
    week_by_week: List[str]
    resources: List[LearningResource]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
