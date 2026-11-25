"""
Pydantic Schemas for AI Planning & Project/Hackathon Guidance.
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PlanMode(str, Enum):
    PROJECT = "project"
    HACKATHON = "hackathon"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class PlanRequest(BaseModel):
    """Input payload for generating an AI project or hackathon plan."""

    mode: PlanMode = Field(
        default=PlanMode.PROJECT,
        description="Guidance mode: 'project' for comprehensive capstone/college guidance or 'hackathon' for MVP/time-boxed competition guidance."
    )
    idea: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The project idea, concept, or hackathon problem statement.",
        examples=["An AI-powered automated grading and feedback assistant for university programming assignments."]
    )
    skill_level: SkillLevel = Field(
        default=SkillLevel.INTERMEDIATE,
        description="Technical skill level of the user or team."
    )
    available_time: str = Field(
        default="3 months",
        description="Time available for development (e.g., '24 hours', '36 hours', '2 weeks', '3 months').",
        examples=["24 hours", "3 months"]
    )
    team_size: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Number of team members working on the project."
    )
    budget: Optional[str] = Field(
        default="Free / Open Source tier",
        description="Budgetary constraints (e.g. 'Free tier only', '$50', 'None')."
    )
    preferred_tech: Optional[List[str]] = Field(
        default=None,
        description="Any specific technologies the user wants to use (e.g., ['Python', 'React'])."
    )


# ---------------------------------------------------------------------------
# Response Component Schemas
# ---------------------------------------------------------------------------

class TechStackItem(BaseModel):
    name: str = Field(..., description="Technology name (e.g. 'FastAPI', 'PostgreSQL')")
    category: str = Field(..., description="Category (Frontend, Backend, Database, AI/ML, Deployment, etc.)")
    reason: str = Field(..., description="Why this technology is specifically recommended for this project")
    alternatives: Optional[List[str]] = Field(default=[], description="Viable alternative technologies")


class AIToolItem(BaseModel):
    tool_name: str = Field(..., description="Name of the AI tool (e.g. 'Cursor', 'Claude 3.5 Sonnet', 'v0.dev')")
    recommended_for: str = Field(..., description="Task stage (e.g. 'UI prototyping', 'Backend agent coding', 'Debugging')")
    purpose: str = Field(..., description="How to utilize this tool effectively in this project")


class RoadmapPhase(BaseModel):
    phase_number: int = Field(..., description="Sequential phase number")
    phase_name: str = Field(..., description="Phase title (e.g. 'Phase 1: Architecture & Data Ingestion')")
    estimated_duration: str = Field(..., description="Time allocation for this phase (e.g. 'Week 1-2' or 'Hours 0-6')")
    goals: List[str] = Field(..., description="Key objectives to achieve in this phase")
    action_items: List[str] = Field(..., description="Concrete, actionable development steps")


class ArchitectureSpec(BaseModel):
    overview: str = Field(..., description="High-level architectural overview")
    frontend_layer: str = Field(..., description="Frontend architecture and user interaction design")
    backend_layer: str = Field(..., description="Backend services, APIs, and business logic layer")
    data_layer: str = Field(..., description="Database, storage, and caching design")
    ai_agent_layer: str = Field(..., description="AI agent orchestration and LLM integration pattern")
    mermaid_diagram: str = Field(..., description="A valid Mermaid diagram string (flowchart TD/LR) representing the architecture")


class JudgingAlignmentItem(BaseModel):
    criterion: str = Field(..., description="Judging criterion (e.g. 'Innovation', 'Technical Depth', 'Feasibility', 'Impact')")
    score_potential: str = Field(..., description="Assessment (e.g. 'High', 'Moderate')")
    how_to_maximize: str = Field(..., description="Specific tactics to impress judges on this criterion")


class TeamTaskAllocation(BaseModel):
    role: str = Field(..., description="Team member role (e.g. 'Full-Stack Lead', 'AI & ML Engineer')")
    responsibilities: List[str] = Field(..., description="Assigned features and responsibilities")
    hours_breakdown: str = Field(..., description="Recommended distribution of time")


class HackathonDetails(BaseModel):
    """Specific guidance components required for hackathons."""
    mvp_core_features: List[str] = Field(..., description="Must-have features for the competition demo")
    cut_features: List[str] = Field(..., description="Features to intentionally omit or defer to save time")
    judging_alignment: List[JudgingAlignmentItem] = Field(..., description="How to align the project with standard judging metrics")
    team_allocation: List[TeamTaskAllocation] = Field(..., description="Recommended task breakdown across team members")
    live_demo_script: List[str] = Field(..., description="Step-by-step walkthrough for a 2-3 minute winning live demo")
    pitch_hook: str = Field(..., description="Compelling 30-second opening statement for judges")
    risk_mitigation: List[str] = Field(..., description="Fallback plans for common live demo failures (e.g. API down, offline backup)")


# ---------------------------------------------------------------------------
# Main Plan Response Schema
# ---------------------------------------------------------------------------

class PlanResponse(BaseModel):
    """Comprehensive structured project or hackathon plan generated by AI."""

    project_title: str = Field(..., description="A concise, professional project title")
    mode: PlanMode = Field(..., description="Mode for which this plan was formulated")
    problem_analysis: str = Field(..., description="Detailed breakdown of the core problem, stakeholders, and pain points")
    recommended_solution: str = Field(..., description="Clear explanation of the proposed solution and unique value proposition")
    technology_stack: List[TechStackItem] = Field(..., description="Recommended technology stack with architectural justification")
    ai_tools: List[AIToolItem] = Field(..., description="Recommended AI developer tools to speed up building")
    architecture: ArchitectureSpec = Field(..., description="System architecture specification with Mermaid diagram")
    roadmap: List[RoadmapPhase] = Field(..., description="Step-by-step execution roadmap")
    estimated_completion_time: str = Field(..., description="Total estimated time to complete")
    hackathon_guidance: Optional[HackathonDetails] = Field(
        default=None,
        description="Detailed hackathon strategy; populated when mode is 'hackathon'"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Execution metadata including model identifier and timestamp"
    )
