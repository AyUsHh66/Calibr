# Calibr ◈ AI Skill Assessment Agent 

## Running Locally (Judges) 

### Prerequisites 
- Docker Desktop installed and running 
- Groq API key (free): console.groq.com 
- Tavily API key (free): app.tavily.com 

### Setup (3 steps) 
1. cp backend/.env.example backend/.env 
2. Add your GROQ_API_KEY and TAVILY_API_KEY to backend/.env 
3. docker-compose up --build 

Open http://localhost:5173

[**Live Demo**](https://calibr-ai.vercel.app) | [**GitHub Repo**](https://github.com/AyUsHh66/Calibr)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com) 
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev) 
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-orange?style=flat)](https://groq.com) 
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com) 
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat)](LICENSE) 

> A resume tells you what someone *claims*. Calibr reveals what they *actually* know. 

--- 

## What It Does 

<div align="center">

<img src="https://img.shields.io/badge/◈-CALIBR-7c6bff?style=for-the-badge&labelColor=0a0a0f&color=7c6bff" alt="Calibr" height="40"/>

# Calibr
### AI-Powered Skill Assessment & Personalised Learning Agent

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-calibr--zeta.vercel.app-7c6bff?style=for-the-badge)](https://calibr-zeta.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-AyUsHh66%2FCalibr-181717?style=for-the-badge&logo=github)](https://github.com/AyUsHh66/Calibr)

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-F55036?style=flat-square)](https://groq.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br/>

> **💡 A resume tells you what someone *claims* to know.**
> **Calibr reveals what they *actually* know.**

<br/>

</div>

---

## 📌 Overview

**Calibr** is a full-stack AI agent that transforms how technical hiring works. Instead of relying on self-reported resume skills, Calibr conducts a real conversational assessment — asking targeted questions, adapting based on answers, detecting confidence signals, and producing a verified proficiency report with a personalised learning roadmap.

Built for **recruiters** who want signal beyond the resume, and **candidates** who want to know exactly where to improve.

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| 🖥️ Frontend | [calibr-zeta.vercel.app](https://calibr-zeta.vercel.app) |
| ⚙️ Backend API | [calibr-production-a797.up.railway.app](https://calibr-production-a797.up.railway.app) |
| 📖 API Docs | [calibr-production-a797.up.railway.app/docs](https://calibr-production-a797.up.railway.app/docs) |

---

## ⚡ Quick Start

### Prerequisites
- [Docker Desktop](https://docker.com/products/docker-desktop) installed and running
- Free API keys (no credit card needed):
  - **Groq** → [console.groq.com](https://console.groq.com) *(14,400 req/day free)*
  - **Tavily** → [app.tavily.com](https://app.tavily.com) *(1,000 searches/month free)*

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/AyUsHh66/Calibr.git
cd Calibr

# 2. Configure environment
cp backend/.env.example backend/.env
# Open backend/.env and add your API keys

# 3. Run everything
docker-compose up --build
```

### ✅ Open http://localhost:5173

> **That's it. One command. No other setup required.**

---

## 🏗️ Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                         C A L I B R                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   ┌──────────────────┐              ┌────────────────────────┐  ║
║   │                  │   REST API   │                        │  ║
║   │   React + Vite   │ ◄──────────► │    FastAPI Backend     │  ║
║   │   Frontend       │    + SSE     │    Python 3.11         │  ║
║   │   :5173          │   Streaming  │    :8000               │  ║
║   │                  │              │                        │  ║
║   │  ┌────────────┐  │              └───────────┬────────────┘  ║
║   │  │  Setup     │  │                          │               ║
║   │  │  Chat      │  │              ┌───────────┼────────────┐  ║
║   │  │  Analysis  │  │              │           │            │  ║
║   │  │  Learning  │  │       ┌──────▼──┐  ┌────▼────┐  ┌────▼┐ ║
║   │  │  Plan      │  │       │  Groq   │  │ Tavily  │  │ DB  │ ║
║   │  │  Recruiter │  │       │ LLaMA   │  │ Search  │  │     │ ║
║   │  └────────────┘  │       │ 3.3 70b │  │   API   │  │SQLite ║
║   └──────────────────┘       └─────────┘  └─────────┘  └─────┘ ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                      AGENT PIPELINE                             ║
║                                                                  ║
║  ┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌───────┐ ║
║  │  1. Extract │   │ 2. Interview │   │ 3. Score │   │4.Plan │ ║
║  │   Skills    │──►│    Loop      │──►│  Skills  │──►│  Gen  │ ║
║  │             │   │  (Dynamic    │   │          │   │       │ ║
║  │  JD+Resume  │   │  Branching)  │   │ 0-100    │   │ PDF   │ ║
║  └─────────────┘   └──────────────┘   └──────────┘   └───────┘ ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🤖 How The Agent Works

### Step 1 — Skill Extraction
Calibr reads the Job Description and resume simultaneously in a single LLM call. It identifies **5–7 key skills** required by the role and tags each as:
- 🔴 `critical` — must-have for the role
- 🟡 `important` — strongly preferred
- 🟢 `nice-to-have` — bonus skills

---

### Step 2 — Dynamic Branching Interview

The agent doesn't ask the same questions to every candidate. It **adapts in real time** based on how well each answer scores:

```
┌─────────────────────────────────────────────────────────────┐
│                  DYNAMIC BRANCHING LOGIC                    │
├──────────────┬──────────────────────────────────────────────┤
│ Score ≥ 70   │ ↑ ESCALATE — system design, edge cases,      │
│  (Strong)    │   "How would you handle this at 10M users?"   │
├──────────────┼──────────────────────────────────────────────┤
│ Score 50–70  │ → PROBE — push for specifics                  │
│  (Mixed)     │   "Give me a concrete real-world example"      │
├──────────────┼──────────────────────────────────────────────┤
│ Score < 50   │ ↓ BASELINE — find the floor                   │
│  (Weak)      │   "Explain the core concept from scratch"      │
└──────────────┴──────────────────────────────────────────────┘
```

---

### Step 3 — Confidence Detection

Every answer is silently analysed for **language patterns** that reveal true knowledge vs performance:

| Signal | What It Means | Language Patterns |
|--------|--------------|-------------------|
| ⚡ **Confident** | Genuine deep knowledge | Specific versions, real project names, trade-off awareness |
| ⚠️ **Hedging** | Knows less than they claim | "I think", "maybe", "I believe", "not 100% sure" |
| 🚨 **Bluffing** | Faking proficiency | Confident tone but zero concrete specifics or examples |

---

### Step 4 — AI / Cheat Detection

Calibr flags answers that may have been **AI-generated or copy-pasted**:

| Flag | Signal |
|------|--------|
| 🟢 Authentic | Personal stories, specific experiences, natural language |
| 🟡 Uncertain | Generic but plausible — could go either way |
| 🔴 AI-assisted | Textbook phrasing, no personal examples, suspiciously perfect grammar |

---

### Step 5 — JD Match Score

After all skills are assessed, Calibr calculates a **weighted JD Match Score**:

```
Match Score = Σ (skill_score × importance_weight) / Σ weights

Where:  critical     = weight 3
        important    = weight 2
        nice-to-have = weight 1
```

Plus a one-line **AI verdict**: *"Strong frontend profile but critical DevOps gaps suggest mid-level fit over the senior role advertised."*

---

### Step 6 — Personalised Learning Plan

For every skill gap (score < 80), Calibr:
1. Live-searches **Tavily** for current, highly-rated courses and resources
2. Generates a **week-by-week roadmap** tailored to the candidate's existing level
3. Prioritises by job impact (critical gaps first)
4. Exports the full report as a **downloadable PDF**

---

## ✨ Feature Overview

| Feature | Description |
|---------|-------------|
| 🎯 Smart Skill Extraction | Auto-identifies key skills from any JD + resume combination |
| 🔀 Dynamic Branching | Questions escalate or simplify based on answer quality |
| 🧠 Confidence Detection | ⚡ Confident / ⚠️ Hedging / 🚨 Bluffing per skill |
| 🚨 AI Suspicion Detection | Flags potentially ChatGPT-assisted answers |
| 📊 JD Match Score | Weighted proficiency score vs job requirements |
| 🤖 AI Verdict | One-line recruiter summary per candidate |
| 📚 Personalised Plan | Week-by-week roadmap with real Tavily-sourced links |
| 👥 Recruiter Dashboard | All candidates ranked by match score |
| 💾 Session Persistence | Resume mid-assessment after page refresh |
| 📄 PDF Export | Download full assessment report |
| 📁 File Upload | Drag and drop PDF / DOCX / TXT resumes |
| 🌊 SSE Streaming | Learning plan streams in card by card in real time |

---

## 🗂️ Project Structure

```
calibr/
├── docker-compose.yml          # One command setup
├── render.yaml                 # Render deployment config
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example            # Template — copy to .env
│   ├── main.py                 # FastAPI app + all routes
│   ├── models.py               # Pydantic + SQLModel schemas
│   ├── db.py                   # SQLite database setup
│   ├── config.py               # Settings via pydantic-settings
│   └── agent/
│       ├── extractor.py        # JD + resume skill extraction
│       ├── interviewer.py      # Dynamic question generation
│       ├── scorer.py           # Proficiency + confidence scoring
│       └── planner.py          # Learning plan + Tavily search
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx             # Main app + routing
        ├── api.js              # All API + SSE calls
        └── components/
            ├── Setup.jsx             # JD + resume input
            ├── Chat.jsx              # Interview chat UI
            ├── Analysis.jsx          # Skill scores + gaps
            ├── LearningPlan.jsx      # Roadmap + PDF download
            └── RecruiterDashboard.jsx # Candidate comparison
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/sessions` | Create session, extract skills |
| `GET` | `/api/sessions/{id}` | Get session state (resume support) |
| `GET` | `/api/sessions/{id}/question` | Get next dynamic question |
| `POST` | `/api/sessions/{id}/answer` | Submit answer, trigger scoring |
| `GET` | `/api/sessions/{id}/analysis` | Full proficiency breakdown |
| `GET` | `/api/sessions/{id}/plan` | SSE stream learning plan |
| `GET` | `/api/sessions/{id}/plan/pdf` | Download PDF report |
| `POST` | `/api/upload` | Upload PDF / DOCX / TXT file |
| `GET` | `/api/recruiter/candidates` | All candidates for dashboard |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + Vite | Fast, modern UI |
| Styling | Custom CSS + Animations | Dark theme, micro-interactions |
| Backend | FastAPI + Python 3.11 | Async REST API + SSE streaming |
| LLM | Groq — LLaMA 3.3 70b | Ultra-fast inference, free tier |
| Search | Tavily API | Real-time course and resource search |
| Database | SQLite via SQLModel | Zero-ops persistent storage |
| PDF | ReportLab | Assessment report generation |
| Container | Docker + Docker Compose | One-command local setup |
| Frontend Deploy | Vercel | Global CDN, free tier |
| Backend Deploy | Railway | Auto-deploy from GitHub, free tier |

---

## 🧠 Architecture Decisions

| Decision | We Chose | We Rejected | Why |
|----------|----------|-------------|-----|
| LLM Provider | Groq | OpenAI | 14,400 free req/day vs paid only |
| Agent Pattern | Direct API calls | LangChain | Full control, no framework overhead, easier to debug |
| Database | SQLite | PostgreSQL | Zero ops for prototype, trivial to swap later |
| Streaming | SSE | WebSockets | Simpler infrastructure, one-way streaming is sufficient |
| Search | Tavily | SerpAPI | JSON output optimised for LLM consumption |
| Containerisation | Docker Compose | Kubernetes | Right-sized for prototype, judges can run with one command |

---

## 🔑 Environment Variables

```bash
# backend/.env.example
GROQ_API_KEY=your_groq_key_here        # console.groq.com
TAVILY_API_KEY=your_tavily_key_here    # app.tavily.com
DATABASE_URL=sqlite:///./calibr.db
CORS_ORIGINS=http://localhost:5173
```

---

## 🚀 Deployment

```
Frontend  →  Vercel   →  calibr-zeta.vercel.app
Backend   →  Railway  →  calibr-production-a797.up.railway.app
Database  →  SQLite   →  persisted on Railway disk
```

---

## 📄 License

MIT © 2025 Calibr — Built with ❤️ using Groq, Tavily, FastAPI and React
 
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