# API Documentation — AI Project & Hackathon Co-Pilot

Complete REST API specification powering the AI Project & Hackathon Co-Pilot platform.

**Base URL:** `http://127.0.0.1:8000/api`  
**Interactive Docs:** `http://127.0.0.1:8000/docs` (Swagger UI)  
**Alternative Docs:** `http://127.0.0.1:8000/redoc` (ReDoc)  

---

## 1. System Health

### `GET /api/health`
Returns runtime system status and AI key readiness.
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "anthropic_configured": true,
  "timestamp": "2026-11-13T06:00:00Z"
}
```

---

## 2. Authentication (`/api/auth`)

### `POST /api/auth/register`
Register a new student developer.
- **Request Body:**
```json
{
  "email": "student@college.edu",
  "password": "Password123!",
  "name": "Alex Rivera",
  "institution": "National Tech University",
  "role": "Student Developer"
}
```
- **Response `201 Created`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "usr-1a2b3c",
    "email": "student@college.edu",
    "name": "Alex Rivera",
    "institution": "National Tech University",
    "role": "Student Developer",
    "created_at": "2026-11-13T06:00:00Z"
  }
}
```

### `POST /api/auth/login`
Authenticate with credentials and receive a signed JWT token.
- **Request Body:** `{"email": "student@college.edu", "password": "Password123!"}`
- **Response `200 OK`:** Returns `access_token` and user profile.

### `GET /api/auth/me` *(Protected)*
Retrieve current authenticated user profile.
- **Headers:** `Authorization: Bearer <token>`
- **Response `200 OK`:** User object without hashed password.

---

## 3. Project Guidance (`/api/project`)

### `POST /api/project/full-blueprint`
Generate a unified 6-dimension capstone blueprint in a single call.
- **Request Body:**
```json
{
  "title": "AI Construction Safety Monitoring",
  "description": "Real-time PPE compliance detection using computer vision.",
  "domain": "AI / Machine Learning",
  "skills": ["Python", "React", "OpenCV"],
  "experience_level": "Intermediate (3rd/4th Year B.Tech Student)",
  "deadline": "3 months",
  "is_team": true,
  "team_size": 3,
  "budget": "Free tier only"
}
```
- **Response `200 OK`:**
```json
{
  "analysis": { ... },
  "technology_stack": { ... },
  "architecture": { ... },
  "roadmap": { ... },
  "coding_prompts": { ... },
  "documentation": { ... }
}
```

### Modular Project Endpoints:
- `POST /api/project/analyze` — Deep feasibility analysis and USP.
- `POST /api/project/tech-stack` — Free-first technology advisor.
- `POST /api/project/architecture` — System architecture and Mermaid diagram.
- `POST /api/project/roadmap` — 9-Phase capstone roadmap.
- `POST /api/project/coding-prompts` — Implementation prompts for Claude & Antigravity IDE.
- `POST /api/project/documentation` — Academic literature survey and IEEE thesis outline.

---

## 4. Hackathon Guidance (`/api/hackathon`)

### `POST /api/hackathon/full-strategy`
Generate an end-to-end competition strategy for 12, 24, 36, or 48-hour hackathons.
- **Request Body:**
```json
{
  "hackathon_name": "Smart City Hackathon 2026",
  "problem_statement": "Detect road hazards in real time from dashcam feeds.",
  "duration": "36 hours",
  "team_size": 3,
  "team_skills": ["Python", "OpenCV", "React"],
  "budget": "Free tier"
}
```
- **Response `200 OK`:** Returns problem analysis, 5+ ideas, evaluation matrix, MoSCoW MVP, time-boxed roadmap (20% reserved buffer), team roles, and multi-tier pitch scripts (30s, 1m, 3m, 5m).

### Modular Hackathon Endpoints:
- `POST /api/hackathon/analyze`
- `POST /api/hackathon/ideas`
- `POST /api/hackathon/evaluate`
- `POST /api/hackathon/mvp`
- `POST /api/hackathon/roadmap`
- `POST /api/hackathon/team`
- `POST /api/hackathon/dev-guidance`
- `POST /api/hackathon/pitch`

---

## 5. Multi-Agent Orchestration (`/api/agent`)

- `POST /api/agent/run` — Executes a LangGraph StateGraph multi-agent chain (`project` or `hackathon`).
- `GET /api/agent/status/{session_id}` — Queries workflow progress, current agent, and results.
- `POST /api/agent/approve/{session_id}` — Human-in-the-loop approval checkpoint resumption.
- `POST /api/agent/retry/{session_id}` — Retries a failed agent node.

---

## 6. Multi-Tenant Project Management (`/api/projects`) *(Protected)*

All endpoints require `Authorization: Bearer <token>`.
- `POST /api/projects` — Create and track a project.
- `GET /api/projects` — List user's active projects.
- `GET /api/projects/{project_id}` — Retrieve project details (ownership verified).
- `PUT /api/projects/{project_id}` — Update project metadata/progress.
- `DELETE /api/projects/{project_id}` — Delete project.
- `POST /api/projects/{project_id}/tasks` — Add milestone task.
- `GET /api/projects/{project_id}/tasks` — List project tasks.
- `PUT /api/projects/{project_id}/tasks/{task_id}` — Update task status (`pending`, `in_progress`, `completed`).

---

## 7. Presentation & Documentation Export (`/api/presentation`)

- `POST /api/presentation/generate-pptx` — Generates and streams an editable 10-slide PowerPoint file (`.pptx`).
- `POST /api/presentation/generate-report` — Generates and streams a 15-section IEEE academic thesis report (`.md`).

---

## 8. Coding Assistance & GitHub Integration (`/api/coding`, `/api/github`)

- `POST /api/coding/generate` — Module starter code and unit test scaffold.
- `POST /api/coding/debug` — Traceback analysis, root cause, and drop-in code fix.
- `POST /api/github/scaffold` — Offline repository generator (README, .gitignore, directory tree, issue templates).
- `GET /api/github/status` — Checks personal access token configuration.
