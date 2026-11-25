"""
Academic Project Documentation Generator (Phase 8).

Compiles a 15-section final-year engineering thesis and capstone report in
standard IEEE-aligned Markdown and HTML formats, ready for viva defense evaluation.
"""

from typing import Dict, Any


class AcademicReportGenerator:
    """Generates comprehensive academic project documentation."""

    @classmethod
    def generate_markdown_report(cls, project_data: Dict[str, Any]) -> str:
        title = project_data.get("title", "AI Project & Hackathon Co-Pilot")
        domain = project_data.get("domain", "AI / Machine Learning")
        author = project_data.get("author", "Student Engineering Team")
        institution = project_data.get("institution", "National Engineering Institute")
        date_str = project_data.get("date", "Academic Year 2025-2026")

        analysis = project_data.get("analysis", {})
        tech_stack = project_data.get("technology_stack", {})
        architecture = project_data.get("architecture", {})
        roadmap = project_data.get("roadmap", {})
        coding_prompts = project_data.get("coding_prompts", {})
        documentation = project_data.get("documentation", {})

        default_mermaid = "graph TD\n    User --> UI[React Frontend]\n    UI --> API[FastAPI Backend]\n    API --> Agents[LangGraph Agents]\n    API --> DB[(Database)]"
        mermaid_code = architecture.get("mermaid_diagram") or default_mermaid

        report = f"""# {title}
## Final-Year Engineering Capstone Project Report
**Domain:** {domain}  
**Author(s):** {author}  
**Institution:** {institution}  
**Date:** {date_str}  

---

## 1. Abstract
{documentation.get('abstract', analysis.get('proposed_solution', 'This project presents an autonomous AI Co-Pilot designed to guide college students and hackathon participants through comprehensive engineering planning.'))}

---

## 2. Problem Statement
{analysis.get('problem_statement', 'Engineering students face steep hurdles selecting modern technology stacks and scoping viable project roadmaps.')}

---

## 3. Project Objectives
The key measurable objectives of this project are:
"""
        for obj in analysis.get("main_objectives", ["Develop backend REST API", "Implement AI orchestration", "Build responsive UI"]):
            report += f"- {obj}\n"

        report += f"""
---

## 4. Existing System & Limitations
Traditional capstone guidance relies on manual ad-hoc advisory with significant limitations:
"""
        for lim in analysis.get("existing_limitations", ["High human latency", "Generic advice not tailored to team skills", "Lack of practical starter code"]):
            report += f"- {lim}\n"

        report += f"""
---

## 5. Proposed System & Innovation
{analysis.get('proposed_solution', 'A multi-agent autonomous system combining LangGraph orchestration with dual-mode project and hackathon guidance.')}

**Unique Selling Proposition (USP):**  
{analysis.get('unique_selling_proposition', 'Deterministic local mocking, free-first tooling recommendations, and instant IEEE documentation generation.')}

---

## 6. Technology Stack & Free-First Tooling
{tech_stack.get('summary', 'Selected for optimal performance, zero cost, and rapid development.')}

### Recommended Components:
| Component | Technology | Category | Role |
|:---|:---|:---|:---|
"""
        for t in tech_stack.get("technologies", [
            {"tech_name": "FastAPI", "category": "Backend", "role": "Async REST API"},
            {"tech_name": "React 19", "category": "Frontend", "role": "Dashboard UI"},
            {"tech_name": "SQLite", "category": "Database", "role": "Relational Storage"},
            {"tech_name": "Claude 3.5", "category": "AI / LLM", "role": "Agent Intelligence"},
        ]):
            if isinstance(t, str):
                report += f"| {t} | {t} | Core Stack | Implementation component |\n"
            elif isinstance(t, dict):
                name = t.get("tech_name") or t.get("technology_name") or t.get("name") or "Component"
                cat = t.get("category", "General")
                role = t.get("role") or t.get("role_in_project") or t.get("why_suitable") or "Component"
                report += f"| {name} | {name} | {cat} | {role} |\n"

        report += f"""
---

## 7. System Architecture & Topology
**Architecture Pattern:** {architecture.get('architecture_pattern', 'Modular Monolith with Decoupled Services')}  

### Architectural Layers:
- **Frontend Layer:** {architecture.get('frontend_layer', 'React 19, TypeScript, Tailwind CSS, Vite')}
- **Backend Layer:** {architecture.get('backend_layer', 'FastAPI asynchronous REST endpoints with Uvicorn')}
- **Data Layer:** {architecture.get('data_layer', 'SQLite / PostgreSQL relational storage with foreign key constraints')}
- **AI Agent Layer:** {architecture.get('ai_pipeline_layer', 'LangGraph Supervisor with 14 specialized agents')}

### Mermaid Architecture Diagram:
```mermaid
{mermaid_code}
```

---

## 8. Main Module Descriptions
"""
        modules = coding_prompts.get("modules", [
            {"module_name": "Module 1: Ingestion & API Layer", "description": "Handles client payloads, validation, and route dispatching."},
            {"module_name": "Module 2: Multi-Agent Intelligence", "description": "Coordinates 14 specialized agents with state tracking."},
            {"module_name": "Module 3: Relational Persistence", "description": "Manages users, projects, tasks, and artifacts."},
            {"module_name": "Module 4: Presentation & Report Generator", "description": "Automates OOXML PPTX and academic report compilation."},
        ])
        for m in modules:
            report += f"### {m.get('module_name')}\n{m.get('description')}\n\n"

        report += f"""
---

## 9. Database Design & Entity Relationships
The relational persistence layer enforces ACID compliance across the following tables:
1. `users`: Stores credentials, names, institutions, and roles.
2. `projects`: Multi-tenant capstone metadata, deadlines, and team sizes.
3. `hackathons`: Sprint challenges, time-boxed constraints, and judging criteria.
4. `tasks`: Milestone tracking with pending/completed status indicators.
5. `workflow_records`: Execution history and multi-agent state logs.

---

## 10. Implementation Methodology
The project follows an iterative Agile engineering lifecycle:
"""
        for phase in roadmap.get("phases", [
            {"phase_number": 1, "phase_name": "Environment & API Baseline", "duration": "Week 1-2"},
            {"phase_number": 2, "phase_name": "Domain Services & Multi-Agents", "duration": "Week 3-6"},
            {"phase_number": 3, "phase_name": "Frontend Dashboard & Security", "duration": "Week 7-9"},
            {"phase_number": 4, "phase_name": "Testing, Review & Deployment", "duration": "Week 10-12"},
        ]):
            if isinstance(phase, str):
                report += f"- **{phase}**\n"
            elif isinstance(phase, dict):
                p_num = phase.get('phase_number', '')
                p_name = phase.get('phase_name', 'Phase')
                p_dur = phase.get('duration') or phase.get('estimated_duration', '')
                dur_str = f" ({p_dur})" if p_dur else ""
                report += f"- **Phase {p_num}: {p_name}**{dur_str}\n"

        report += f"""
---

## 11. Testing & Quality Assurance Strategy
Testing adheres to strict verification principles:
- **Zero Paid Credit Leakage:** All external AI interactions are mocked using deterministic AsyncMock fixtures.
- **Unit & Integration Coverage:** 62+ automated tests covering security, tokens, routing, and database transactions.
- **Continuous Execution:** Full test suite verified in under 10 seconds locally.

---

## 12. Expected Outcomes & Experimental Results
"""
        for outcome in analysis.get("expected_outcomes", [
            "Sub-100ms API response latency on local development environments.",
            "100% automated test pass rate with zero dependency failures.",
            "Complete student capstone defense delivered with verified code and documentation.",
        ]):
            report += f"- {outcome}\n"

        report += f"""
---

## 13. Future Enhancements
1. Real-time WebSockets streaming for live agent reasoning visualization.
2. Local Small Language Model (SLM) integration for offline edge inference.
3. Automated GitHub CI/CD workflow generator.

---

## 14. Academic Conclusion
{documentation.get('conclusion_and_future_work', 'This capstone project successfully demonstrates an autonomous AI Co-Pilot that coordinates 14 specialized agents to solve engineering hurdles for college students and hackathon competitors.')}

---

## 15. References & Literature Review
1. Anthropic Claude API Documentation & Tool Use Guidelines (2025).
2. LangChain & LangGraph Multi-Agent Orchestration Frameworks (2024-2025).
3. FastAPI: Modern, High-Performance Web Framework for Python (Tiangolo, 2024).
4. React 19: Architecture, Concurrent Rendering, and Component Design (Meta, 2025).
"""
        return report
