# AI Project & Hackathon Co-Pilot (Powered by Google Gemini)

[![AI Provider: Google Gemini](https://img.shields.io/badge/AI%20Provider-Google%20Gemini-4285F4.svg)](https://ai.google.dev)
[![Model: Gemini 3.5 Flash](https://img.shields.io/badge/Model-Gemini%203.5%20Flash-34A853.svg)](https://ai.google.dev)
[![Tests: 74 Passing](https://img.shields.io/badge/Tests-74%20Passing-brightgreen.svg)](https://pytest.org)
[![FastAPI: 0.162](https://img.shields.io/badge/FastAPI-0.162-009688.svg)](https://fastapi.tiangolo.com)
[![React: 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Tailwind: v4](https://img.shields.io/badge/Tailwind%20CSS-v4-38B2AC.svg)](https://tailwindcss.com)
[![LangGraph](https://img.shields.io/badge/Multi--Agent-LangGraph%20Compatible-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An autonomous, multi-agent AI co-pilot powered by **Google Gemini** (with official `google-genai` SDK integration) designed for college final-year engineering capstone projects and high-stakes 12-48 hour hackathons. Turn problem statements into production architectures, free-first technology recommendations, 9-phase roadmaps, copy-ready coding prompts, viva defense presentations (.pptx), and IEEE-aligned thesis papers in seconds.

---

## 🌟 Key Features

### 1. Dual-Mode Intelligence System
- **Capstone Project Guidance Mode:** Comprehensive 9-phase engineering blueprint generation, system architecture with Mermaid topology, free-first technology advising, coding prompts, and academic thesis outlines.
- **Hackathon Sprint Mode (12h, 24h, 36h, 48h):** Generates 5+ distinct ideas, weighted feasibility scoring matrix, MoSCoW MVP scoping with live presentation failure safeguards, team task allocation, and multi-tier pitch decks (30s, 1m, 3m, 5m) with judge defense Q&A.

### 2. Multi-Agent Intelligence (14 Specialized Agents)
Supervisor-based orchestration with in-tree LangGraph `StateGraph` support:
- **Project Guidance Agents:** `project_analyzer`, `technology_advisor`, `architecture`, `roadmap`, `coding`, `documentation`, `testing`
- **Hackathon Agents:** `hackathon_analyzer`, `idea_generator`, `idea_evaluation`, `mvp_planning`, `team_allocation`, `dev_guidance`, `pitch`

### 3. Professional SaaS Dashboard (React 19 + Tailwind v4)
- **7 Fully Interactive Views:** Landing Page, Authentication, Dashboard with KPI stats, Project Guidance, Hackathon Sprint Engine, Interactive Project Workspace & Tasks, and Settings.
- Responsive modern dark-mode layout, live health status monitoring, and Markdown/JSON deliverable exporters.

### 4. Multi-Tenant Relational Persistence & Security
- **Security:** Standard-library PBKDF2-HMAC-SHA256 password hashing (100,000 iterations) and RFC 7519 HMAC-SHA256 JWT tokens.
- **Data Persistence:** Relational SQLite engine (`backend/data/copilot.db`) storing Users, Projects, Tasks, Artifacts, and Workflow Records with strict multi-tenant isolation.

### 5. Automated Presentation (.pptx) & Academic Report Generation
- **PowerPoint Exporter:** Generates 10-slide editable OOXML Microsoft PowerPoint (.pptx) presentations natively without external C-extensions.
- **Academic Report Exporter:** Compiles complete 15-section IEEE-aligned thesis papers ready for college viva defense.

### 6. Coding Assistant & GitHub Scaffolder
- Starter code and unit test scaffold generator.
- Stack trace error diagnostician with drop-in code fixes.
- Offline-first GitHub repository scaffolding (README with badges, `.gitignore`, directory layout, milestone issue templates).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js v20+ and npm

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/ai-project-copilot.git
cd ai-project-copilot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Configure environment variables (Add your Google Gemini API Key)
cp .env.example backend/.env
# In backend/.env:
# AI_PROVIDER=gemini
# GEMINI_API_KEY=your_gemini_api_key_here
# GEMINI_MODEL=gemini-3.5-flash

# Start FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be live at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Frontend Setup
```bash
# In a new terminal:
cd frontend

# Install frontend dependencies
npm install

# Start Vite dev server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Running Automated Tests

All tests run completely offline using deterministic fixtures with **$0.00** API credit usage:
```bash
# Run complete test suite (70 tests across Phases 1-9)
python -m pytest backend/tests -v
```

---

## 📁 Repository Structure
```
ai-project-copilot/
├── .env.example                      # Environment variable template
├── .gitignore                        # Git exclusion rules
├── pytest.ini                        # pytest configuration
├── Dockerfile.backend                # Multi-stage Python backend container
├── Dockerfile.frontend               # Nginx frontend container
├── docker-compose.yml                # Full-stack Docker orchestration
├── render.yaml                       # Cloud deployment configuration
├── vercel.json                       # Frontend edge routing
├── backend/
│   ├── requirements.txt              # Core Python dependencies
│   ├── app/
│   │   ├── main.py                   # FastAPI application entrypoint
│   │   ├── config.py                 # Configuration loader
│   │   ├── agents/                   # 14 specialized agents & LangGraph StateGraph
│   │   ├── api/routes/               # REST API route controllers
│   │   ├── auth/                     # PBKDF2 hashing & RFC 7519 JWT security
│   │   ├── db/                       # Relational SQLite database engine
│   │   ├── schemas/                  # Pydantic v2 data models
│   │   └── services/                 # Business logic, Claude, PPTX & Report engines
│   └── tests/                        # 70 automated tests
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── App.tsx                   # Main router & session state
        ├── components/               # Navbar & reusable components
        ├── pages/                    # 7 SaaS views
        ├── services/api.ts           # Typed backend client
        └── types/index.ts            # Data contracts
```

---

## 📄 License
MIT License — Free to use, adapt, and distribute for college projects, hackathons, and research.
