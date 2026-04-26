# Calibr ◈ AI Skill Assessment Agent 

[**Live Demo**](https://calibr-ai.vercel.app) | [**GitHub Repo**](https://github.com/AyUsHh66/Calibr)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com) 
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev) 
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-orange?style=flat)](https://groq.com) 
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com) 
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat)](LICENSE) 

> A resume tells you what someone *claims*. Calibr reveals what they *actually* know. 

--- 

## What It Does 

Calibr is an AI agent that: 
1. **Extracts** real required skills from any job description 
2. **Interviews** candidates conversationally with dynamic branching questions 
3. **Scores** proficiency 0–100 per skill with confidence detection 
4. **Generates** a personalised week-by-week learning roadmap 
5. **Flags** potential AI-assisted or inauthentic answers 

--- 

## Quick Start (1 command) 

### Prerequisites 
- Docker + Docker Compose installed 
- Groq API key (free at console.groq.com) 
- Tavily API key (free at app.tavily.com) 

### Setup 
```bash
git clone https://github.com/AyUsHh66/calibr.git
cd calibr 
cp backend/.env.example backend/.env 
```

# Add your keys to backend/.env: 
# GROQ_API_KEY=gsk_... 
# TAVILY_API_KEY=tvly-... 

```bash
docker-compose up --build 
```

Open http://localhost:5173 

--- 

## Architecture 

```
Browser (React + Vite :5173) 
        │ 
        │  REST + SSE 
        ▼ 
FastAPI Backend (:8000) 
        │ 
        ├──► Groq API (LLaMA 3.3 70b) 
        │      Skill extraction 
        │      Question generation  
        │      Dynamic branching 
        │      Scoring + confidence detection 
        │ 
        ├──► Tavily Search API 
        │      Real course links 
        │      Up-to-date resources 
        │ 
        └──► SQLite (via SQLModel) 
               Session persistence 
               Resume mid-assessment 
```

--- 

## How The Agent Works 

### 1. Skill Extraction 
Parses JD + resume in one Groq call. Returns 5–7 skills 
tagged as critical / important / nice-to-have. 

### 2. Dynamic Branching Interview 
Each skill gets 2–3 targeted questions. 
After every answer, the agent scores and branches: 

- **Score ≥ 70**  →  Escalate: "Design this at 10M users scale..." 
- **Score 50–70** →  Probe: "Give me a concrete real-world example..." 
- **Score < 50**  →  Baseline: "Explain the core concept from scratch..." 

### 3. Confidence Detection 
Every answer is analysed for language patterns: 

- ⚡ **Confident**  — specific versions, real projects, trade-off awareness 
- ⚠️ **Hedging**   — "I think", "maybe", "I believe", "not sure" 
- 🚨 **Bluffing**  — confident tone, zero concrete specifics 

### 4. AI Suspicion Detection 
Flags potentially ChatGPT-assisted answers: 
- 🟢 **Authentic**   — personal stories, specific experiences 
- 🟡 **Uncertain**   — generic but plausible 
- 🔴 **AI-assisted** — textbook phrasing, no personal examples 

### 5. Learning Plan Generation 
- Filters skills by gap (score < 80) 
- Searches Tavily for current, real course links 
- Generates week-by-week roadmap via Groq 
- Exports as PDF 

--- 

## API Endpoints 

| Method | Endpoint | Description | 
|--------|----------|-------------| 
| POST | /api/sessions | Create session, extract skills | 
| GET | /api/sessions/{id} | Get session state (for resume) | 
| GET | /api/sessions/{id}/question | Get next question | 
| POST | /api/sessions/{id}/answer | Submit answer, get score | 
| GET | /api/sessions/{id}/analysis | Full skill breakdown | 
| GET | /api/sessions/{id}/plan | SSE stream learning plan | 
| GET | /api/sessions/{id}/plan/pdf | Download PDF report | 
| POST | /api/upload | Upload PDF/DOCX/TXT resume | 
| GET | /api/recruiter/candidates | All assessed candidates | 

--- 

## Architecture Decisions 

| Decision | Choice | Why | 
|----------|--------|-----| 
| LLM | Groq LLaMA 3.3 70b | 10x faster than GPT-4, generous free tier | 
| DB | SQLite via SQLModel | Zero ops, trivial to swap to Postgres later | 
| Streaming | SSE not WebSockets | Simpler infra, sufficient for one-way stream | 
| Agent | Direct API calls not LangChain | Full control, easier to debug, no framework overhead | 
| Search | Tavily | Purpose-built for AI agents, clean JSON results | 

--- 

## .env.example 

```
GROQ_API_KEY=gsk_your_key_here 
TAVILY_API_KEY=tvly_your_key_here 
DATABASE_URL=sqlite:///./data/calibr.db 
CORS_ORIGINS=http://localhost:5173,https://your-frontend-url.vercel.app
```

--- 

## Local Development (without Docker) 

### Backend 
```bash
cd backend 
pip install -r requirements.txt 
uvicorn main:app --reload --port 8000 
```

### Frontend 
```bash
cd frontend 
npm install 
npm run dev 
```

--- 

## License 
MIT