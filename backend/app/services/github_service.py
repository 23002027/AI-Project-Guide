"""
GitHub Integration Service (Phase 9).

Provides repository scaffolding, README generation, directory layout recommendations,
and GitHub REST API connectivity when credentials are configured.
Enforces safety rules: never deletes or modifies remote repositories without explicit user authorization.
"""

import os
from typing import Optional, Dict, Any, List
import httpx

from backend.app.schemas.coding_assistant import (
    GitHubScaffoldRequest,
    GitHubScaffoldResponse,
    GitHubIssueTemplate,
)


class GitHubService:
    """Service for GitHub repository scaffolding and API interaction."""

    GITHUB_API_BASE = "https://api.github.com"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "").strip()

    @property
    def is_configured(self) -> bool:
        """Check whether a valid GitHub personal access token is configured."""
        return bool(self.token and self.token != "your_github_token_here")

    def generate_scaffold(self, req: GitHubScaffoldRequest) -> GitHubScaffoldResponse:
        """
        Generate a complete repository package: README.md, .gitignore,
        directory layout, and GitHub issue templates. Runs 100% offline.
        """
        tech_list = ", ".join(req.tech_stack)
        readme = f"""# {req.project_title}

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React: 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)

{req.description}

---

## 🛠️ Tech Stack & Architecture
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Frontend:** React 19, TypeScript, Tailwind CSS v4, Vite
- **AI Intelligence:** Anthropic Claude 3.5 Sonnet + LangGraph Supervisor
- **Database:** SQLite / PostgreSQL Relational Storage with JWT Authentication

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher
- Node.js v20+ and npm

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/{req.repo_name}.git
cd {req.repo_name}

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env

# Run FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend Setup
```bash
# Open new terminal in frontend directory
cd frontend

# Install frontend dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend will be live at [http://localhost:3000](http://localhost:3000).

---

## 🧪 Running Automated Tests
```bash
# Run pytest with offline mocked fixtures
python -m pytest backend/tests -v
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
"""

        gitignore = """# Python & Virtual Environments
__pycache__/
*.py[cod]
*$py.class
.venv/
env/
venv/
*.egg-info/
dist/
build/

# Node & Frontend
node_modules/
frontend/dist/
.npm
*.tsbuildinfo

# Environment & Secrets
.env
*.local
copilot.db
*.sqlite3

# IDE & OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Testing & Coverage
.pytest_cache/
.coverage
htmlcov/
"""

        tree = f"""{req.repo_name}/
├── .env.example
├── .gitignore
├── README.md
├── pytest.ini
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── agents/
│   │   ├── api/routes/
│   │   ├── auth/
│   │   ├── db/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
│       ├── test_health.py
│       ├── test_agent_orchestration.py
│       └── test_database_and_auth.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── components/
        ├── pages/
        ├── services/
        └── types/
"""

        issues = [
            GitHubIssueTemplate(
                title="Milestone 1: Setup FastAPI baseline and health check",
                labels=["backend", "setup"],
                body="Configure virtual environment, setup `.env.example`, implement `/api/health`, and verify baseline tests.",
            ),
            GitHubIssueTemplate(
                title="Milestone 2: Implement multi-agent supervisor orchestrator",
                labels=["ai", "langgraph"],
                body="Register specialized agents in StateGraph engine and handle workflow pause/resume approval checkpoints.",
            ),
            GitHubIssueTemplate(
                title="Milestone 3: Build React dashboard and guidance forms",
                labels=["frontend", "ui"],
                body="Implement responsive landing page, project guidance forms, and real-time task manager in React 19.",
            ),
            GitHubIssueTemplate(
                title="Milestone 4: Setup JWT authentication and project CRUD",
                labels=["security", "database"],
                body="Implement PBKDF2 password hashing, RFC 7519 JWT verification, and multi-tenant project isolation.",
            ),
            GitHubIssueTemplate(
                title="Milestone 5: Final capstone viva presentation and reports",
                labels=["documentation"],
                body="Generate automated 10-slide OOXML PowerPoint presentation (.pptx) and 15-section IEEE thesis paper.",
            ),
        ]

        setup_cmds = [
            "git init",
            "git add .",
            'git commit -m "Initial commit: AI Project & Hackathon Co-Pilot scaffold"',
            f"git branch -M main",
            f"# Connect remote: git remote add origin https://github.com/your-username/{req.repo_name}.git",
            "# Push: git push -u origin main",
        ]

        return GitHubScaffoldResponse(
            repo_name=req.repo_name,
            github_configured=self.is_configured,
            readme_content=readme,
            suggested_gitignore=gitignore,
            suggested_directory_tree=tree,
            suggested_issues=issues,
            setup_commands=setup_cmds,
        )

    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Fetch authenticated GitHub user profile if token is configured."""
        if not self.is_configured:
            return None

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.GITHUB_API_BASE}/user", headers=headers)
            if resp.status_code == 200:
                return resp.json()
            return None
