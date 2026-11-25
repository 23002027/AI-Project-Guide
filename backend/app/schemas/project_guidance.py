"""
Pydantic Schemas for Full Project Guidance Mode.
Defines structured request and response contracts for project analysis,
technology recommendations, architecture generation, roadmaps,
coding prompts, academic documentation, and deployment strategies.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class ProjectDomain(str, Enum):
    AI_ML = "AI / Machine Learning"
    WEB_DEV = "Full-Stack Web Development"
    HEALTHCARE = "Healthcare & Biomedical"
    AGRICULTURE = "AgriTech & Smart Farming"
    FINANCE = "FinTech & Blockchain"
    EDUCATION = "EdTech & Learning Platforms"
    IOT_EMBEDDED = "IoT & Smart Devices"
    CYBERSECURITY = "Cybersecurity & Privacy"
    GENERAL = "General Engineering / Other"


class ExperienceLevel(str, Enum):
    BEGINNER = "Beginner (1st/2nd Year Student)"
    INTERMEDIATE = "Intermediate (3rd/4th Year B.Tech Student)"
    ADVANCED = "Advanced (Experienced Developer)"


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ProjectIdeaInput(BaseModel):
    """Input payload describing a student's project idea and constraints."""
    title: str = Field(..., min_length=3, max_length=200, description="Project title or working name")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed concept, problem, or vision")
    domain: ProjectDomain = Field(default=ProjectDomain.AI_ML, description="Primary domain of the project")
    skills: List[str] = Field(default=["Python"], description="Programming languages or frameworks the student/team knows")
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.INTERMEDIATE, description="Technical proficiency level")
    budget: Optional[str] = Field(default="Free / Open Source tier", description="Budget limits (e.g. 'Free tier only', '$100')")
    deadline: str = Field(default="3 months", description="Available timeframe (e.g. '6 weeks', '3 months', '1 semester')")
    is_team: bool = Field(default=False, description="Whether this is an individual or team capstone project")
    team_size: int = Field(default=1, ge=1, le=20, description="Number of team members")

    @classmethod
    def from_flexible_dict(cls, data: dict) -> "ProjectIdeaInput":
        """Convert flexible key inputs (e.g. project_title -> title, skills string -> list)."""
        d = dict(data)
        if "title" not in d and "project_title" in d:
            d["title"] = d["project_title"]
        if "programming_skills" in d and "skills" not in d:
            raw_skills = d["programming_skills"]
            if isinstance(raw_skills, str):
                d["skills"] = [s.strip() for s in raw_skills.split(",") if s.strip()]
            elif isinstance(raw_skills, list):
                d["skills"] = raw_skills
        if "is_team_project" in d and "is_team" not in d:
            d["is_team"] = bool(d["is_team_project"])

        # Normalize domain variations
        if "domain" in d and isinstance(d["domain"], str):
            dom = d["domain"].lower().strip()
            if any(k in dom for k in ["ai", "ml", "machine learning", "deep learning"]):
                d["domain"] = ProjectDomain.AI_ML.value
            elif any(k in dom for k in ["web", "frontend", "backend", "full-stack", "fullstack"]):
                d["domain"] = ProjectDomain.WEB_DEV.value
            elif any(k in dom for k in ["health", "biomedical", "medical"]):
                d["domain"] = ProjectDomain.HEALTHCARE.value
            elif any(k in dom for k in ["agri", "farm", "crop"]):
                d["domain"] = ProjectDomain.AGRICULTURE.value
            elif any(k in dom for k in ["fin", "bank", "crypto", "blockchain"]):
                d["domain"] = ProjectDomain.FINANCE.value
            elif any(k in dom for k in ["ed", "learn", "teach", "school"]):
                d["domain"] = ProjectDomain.EDUCATION.value
            elif any(k in dom for k in ["iot", "embed", "hardware", "sensor"]):
                d["domain"] = ProjectDomain.IOT_EMBEDDED.value
            elif any(k in dom for k in ["cyber", "security", "privacy"]):
                d["domain"] = ProjectDomain.CYBERSECURITY.value
            else:
                found = False
                for pd in ProjectDomain:
                    if dom == pd.value.lower():
                        d["domain"] = pd.value
                        found = True
                        break
                if not found:
                    d["domain"] = ProjectDomain.GENERAL.value

        # Normalize experience_level variations
        if "experience_level" in d and isinstance(d["experience_level"], str):
            exp = d["experience_level"].lower().strip()
            if "beginner" in exp:
                d["experience_level"] = ExperienceLevel.BEGINNER.value
            elif "advanced" in exp:
                d["experience_level"] = ExperienceLevel.ADVANCED.value
            elif "intermediate" in exp:
                d["experience_level"] = ExperienceLevel.INTERMEDIATE.value
            else:
                d["experience_level"] = ExperienceLevel.INTERMEDIATE.value

        return cls(**d)

# Alias for backward compatibility
ProjectInput = ProjectIdeaInput


# ---------------------------------------------------------------------------
# Feature 1: Project Idea Analysis Schemas
# ---------------------------------------------------------------------------

class ProjectAnalysisResponse(BaseModel):
    """Deep academic and engineering analysis of the project idea."""
    project_title: str
    domain: str
    problem_statement: str = Field(..., description="Clear definition of the problem being solved")
    existing_limitations: List[str] = Field(..., description="Shortcomings of current solutions or existing work")
    proposed_solution: str = Field(..., description="How the proposed system solves the problem")
    target_users: List[str] = Field(..., description="Primary beneficiaries and stakeholders")
    main_objectives: List[str] = Field(..., description="Core measurable engineering objectives")
    expected_outcomes: List[str] = Field(..., description="Concrete deliverables and tangible results")
    unique_selling_proposition: str = Field(..., description="What makes this project innovative and standout for evaluators")
    innovation_opportunities: List[str] = Field(..., description="High-impact research or engineering additions")
    feasibility_assessment: str = Field(..., description="Evaluation of timeline, resources, and technical viability")
    project_complexity: str = Field(..., description="Complexity rating: Moderate, High, or Advanced")
    follow_up_questions: List[str] = Field(default=[], description="Clarifying questions if requirements are ambiguous")


# ---------------------------------------------------------------------------
# Features 2 & 3: Technology & AI Tool Recommendations
# ---------------------------------------------------------------------------

class TechRecommendationDetail(BaseModel):
    technology_name: str
    category: str = Field(..., description="Frontend, Backend, Database, AI/ML Model, Auth, Hosting, Testing, etc.")
    why_suitable: str = Field(..., description="Why this tool fits the student's skill and deadline")
    role_in_project: str = Field(..., description="Exact functional responsibility inside the application")
    implementation_guide: str = Field(..., description="Step-by-step instructions on getting started")
    cost_tier: str = Field(..., description="Free, Freemium, or Paid with exact pricing context")
    alternatives: List[str] = Field(default=[], description="Viable alternative options")


class AIToolAdvisorItem(BaseModel):
    tool_name: str = Field(..., description="E.g. Claude, Antigravity, GitHub Copilot, v0.dev, Cursor")
    development_activity: str = Field(..., description="UI Design, Backend Agents, Debugging, Documentation, Testing")
    how_to_use: str = Field(..., description="Practical instructions on using this AI tool effectively")
    when_to_use: str = Field(..., description="At which project milestone to use it")
    free_alternative: str = Field(..., description="Zero-cost alternative if tool requires payment")


class TechStackAdvisorResponse(BaseModel):
    """Curated technology stack and AI tooling recommendations."""
    project_title: str
    technology_recommendations: List[TechRecommendationDetail]
    ai_tool_advisors: List[AIToolAdvisorItem]
    rationale_summary: str = Field(..., description="Executive summary explaining the architectural synergy of the chosen stack")


# ---------------------------------------------------------------------------
# Feature 4: System Architecture Schemas
# ---------------------------------------------------------------------------

class APIEndpointSuggestion(BaseModel):
    method: str = Field(..., description="GET, POST, PUT, DELETE")
    path: str = Field(..., description="URL path (e.g. /api/analysis)")
    description: str = Field(..., description="Purpose and payload details")


class ModuleArchitectureItem(BaseModel):
    module_name: str
    responsibility: str
    technologies_used: List[str]
    inputs: str
    outputs: str


class ArchitectureGeneratorResponse(BaseModel):
    """Complete architectural blueprint and diagram specifications."""
    project_title: str
    high_level_overview: str
    frontend_backend_flow: str
    database_architecture: str
    module_breakdown: List[ModuleArchitectureItem]
    api_endpoint_suggestions: List[APIEndpointSuggestion]
    data_flow_explanation: str
    mermaid_diagram: str = Field(..., description="Valid Mermaid flowchart syntax")


# ---------------------------------------------------------------------------
# Features 5 & 9: Complete Development Roadmap & Deployment Schemas
# ---------------------------------------------------------------------------

class RoadmapPhaseDetail(BaseModel):
    phase_number: int
    phase_title: str
    estimated_duration: str
    tasks: List[str]
    dependencies: List[str]
    required_tools: List[str]
    expected_output: str
    completion_checklist: List[str]


class DeploymentGuidance(BaseModel):
    hosting_platform: str
    environment_variables_checklist: List[str]
    step_by_step_deployment: List[str]
    testing_strategy: List[str]
    maintenance_practices: List[str]


class DevelopmentRoadmapResponse(BaseModel):
    """9-Phase practical development roadmap aligned with college milestones."""
    project_title: str
    total_estimated_duration: str
    phases: List[RoadmapPhaseDetail]
    deployment_and_testing: DeploymentGuidance


# ---------------------------------------------------------------------------
# Features 6 & 7: Module Coding & AI Prompts Schemas
# ---------------------------------------------------------------------------

class ModuleCodingStep(BaseModel):
    module_name: str
    purpose: str
    folder_structure: str
    implementation_steps: List[str]
    example_code_snippet: str
    required_dependencies: List[str]
    testing_instructions: str
    common_errors_and_solutions: List[str]


class AICopyReadyPrompt(BaseModel):
    target_tool: str = Field(..., description="Claude, Antigravity, GitHub Copilot, Cursor, etc.")
    use_case: str = Field(..., description="Backend setup, UI Component, DB Schema, Debugging, Deployment")
    prompt_text: str = Field(..., description="Full, context-rich, copy-ready prompt")


class AICodingPromptsResponse(BaseModel):
    """Module-wise coding walkthrough and external AI tool prompts."""
    project_title: str
    module_walkthroughs: List[ModuleCodingStep]
    copy_ready_prompts: List[AICopyReadyPrompt]
    modules: Optional[List[Dict[str, Any]]] = None

    @model_validator(mode="after")
    def populate_modules(self) -> "AICodingPromptsResponse":
        if self.modules is None:
            self.modules = [
                {
                    "module_name": w.module_name,
                    "description": w.purpose,
                    "claude_coding_prompt": (
                        w.example_code_snippet
                        or (self.copy_ready_prompts[idx % len(self.copy_ready_prompts)].prompt_text if self.copy_ready_prompts else "")
                    )
                }
                for idx, w in enumerate(self.module_walkthroughs)
            ]
        return self


# ---------------------------------------------------------------------------
# Feature 8: Research and Documentation Schemas
# ---------------------------------------------------------------------------

class ProjectDocumentationResponse(BaseModel):
    """Complete final-year college project report & research synopsis."""
    project_title: str
    abstract: str
    introduction: str
    problem_statement: str
    literature_review_outline: List[str]
    objectives: List[str]
    methodology: str
    proposed_architecture_summary: str
    implementation_plan_summary: str
    testing_methodology: str
    results_section_template: str
    conclusion: str
    future_scope: List[str]


# ---------------------------------------------------------------------------
# Master Blueprint Schema
# ---------------------------------------------------------------------------

class FullProjectBlueprintResponse(BaseModel):
    """Complete unified project guidance blueprint combining all features."""
    project_title: str
    analysis: ProjectAnalysisResponse
    technology_stack: TechStackAdvisorResponse
    architecture: ArchitectureGeneratorResponse
    roadmap: DevelopmentRoadmapResponse
    coding_and_prompts: AICodingPromptsResponse
    coding_prompts: Optional[AICodingPromptsResponse] = None
    documentation: ProjectDocumentationResponse
    metadata: Dict[str, Any] = Field(default_factory=dict)
