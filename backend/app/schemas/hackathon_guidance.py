"""
Pydantic Schemas for Hackathon Guidance Mode (Phase 4).
Defines contracts for hackathon problem analysis, multi-idea generation,
weighted idea evaluation, MVP scoping, time-boxed roadmaps,
team task allocation, and multi-tier pitch decks.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input Schemas
# ---------------------------------------------------------------------------

class TeamMemberSkill(BaseModel):
    member_name: str = Field(..., description="Name or identifier of team member (e.g. Member 1, Alex)")
    role_preference: Optional[str] = Field(default=None, description="Preferred role (Frontend, Backend, AI/ML, Design, Pitch)")
    skills: List[str] = Field(default=[], description="Skills and tools known by this member")


class JudgingCriterionInput(BaseModel):
    criterion_name: str = Field(..., description="Criterion name (e.g. 'Innovation', 'Technical Complexity')")
    weight_percentage: Optional[float] = Field(default=None, description="Weight percentage (e.g. 25.0 for 25%)")
    description: Optional[str] = Field(default=None, description="Description of the judging rule or expectation")


class HackathonIdeaItem(BaseModel):
    idea_id: int
    project_title: str
    problem_solved: str
    proposed_solution: str
    innovation_angle: str
    key_features: List[str]
    suggested_tech_stack: List[str]
    technical_feasibility: str = Field(..., description="Feasibility within the hackathon time frame (High/Moderate)")
    expected_impact: str
    demo_potential: str = Field(..., description="Visual appeal and wow-factor during a 2-3 minute live demo")


class HackathonInput(BaseModel):
    """Input payload describing the hackathon problem and team constraints."""
    hackathon_name: str = Field(default="Hackathon Competition", description="Name of the hackathon")
    problem_statement: str = Field(..., min_length=15, max_length=10000, description="The problem statement text or document excerpt")
    domain: Optional[str] = Field(default="AI / Machine Learning", description="Hackathon domain or track")
    duration: str = Field(default="24 hours", description="Hackathon duration (e.g. '12 hours', '24 hours', '36 hours', '48 hours')")
    team_size: int = Field(default=3, ge=1, le=10, description="Number of team members")
    team_skills: List[str] = Field(default=["Python", "React"], description="Aggregated team technical skills")
    team_members: Optional[List[TeamMemberSkill]] = Field(default=None, description="Optional individual member profiles")
    experience_level: str = Field(default="Intermediate", description="Beginner, Intermediate, or Advanced")
    available_technologies: Optional[List[str]] = Field(default=None, description="Technologies or hardware available to the team")
    budget: Optional[str] = Field(default="Free / Open Source tier only", description="Optional budget limit (default zero-cost)")
    judging_criteria: Optional[List[JudgingCriterionInput]] = Field(default=None, description="Official hackathon judging criteria if available")
    candidate_ideas: Optional[List[HackathonIdeaItem]] = Field(default=None, description="Optional pre-generated ideas to evaluate, avoiding duplicate AI calls")


# ---------------------------------------------------------------------------
# Feature 2: Problem Statement Analyzer Schemas
# ---------------------------------------------------------------------------

class HackathonAnalysisResponse(BaseModel):
    """Structured analysis of the hackathon problem statement and rules."""
    hackathon_name: str
    problem_summary: str = Field(..., description="Clear summary of the underlying problem")
    target_users: List[str] = Field(..., description="Primary user personas affected by the problem")
    existing_challenges: List[str] = Field(..., description="Current limitations and why existing solutions fall short")
    core_requirements: List[str] = Field(..., description="Must-fulfill requirements extracted from the prompt")
    expected_solution: str = Field(..., description="Characteristics of a winning solution")
    constraints: List[str] = Field(..., description="Time, technical, and resource constraints")
    potential_opportunities: List[str] = Field(..., description="High-impact innovation angles to impress judges")


# ---------------------------------------------------------------------------
# Feature 3: Hackathon Idea Generator Schemas
# ---------------------------------------------------------------------------

class HackathonIdeasResponse(BaseModel):
    """At least 5 genuinely distinct hackathon project concepts."""
    hackathon_name: str
    ideas: List[HackathonIdeaItem] = Field(..., min_length=5, description="At least 5 distinct project ideas")


# ---------------------------------------------------------------------------
# Feature 4: Idea Evaluation & Scoring Schemas
# ---------------------------------------------------------------------------

class IdeaScoreBreakdown(BaseModel):
    idea_id: int
    project_title: str
    problem_relevance: float = Field(..., ge=0, le=10, description="Score 0-10 on alignment with problem statement")
    innovation: float = Field(..., ge=0, le=10, description="Score 0-10 on originality and uniqueness")
    technical_feasibility: float = Field(..., ge=0, le=10, description="Score 0-10 on ability to build in allotted hours")
    social_business_impact: float = Field(..., ge=0, le=10, description="Score 0-10 on real-world utility")
    demo_potential: float = Field(..., ge=0, le=10, description="Score 0-10 on visual impressiveness to judges")
    time_feasibility: float = Field(..., ge=0, le=10, description="Score 0-10 on completion within deadline")
    weighted_total_score: float = Field(..., description="Final composite score")
    strengths: List[str]
    risks_and_pitfalls: List[str]


class IdeaEvaluationResponse(BaseModel):
    """Objective scoring and recommendation of hackathon concepts."""
    scoring_method: str = Field(..., description="Official criteria weights or Default Balanced Matrix")
    ranked_ideas: List[IdeaScoreBreakdown]
    recommended_idea_id: int
    recommended_idea_title: str
    recommendation_rationale: str = Field(..., description="Why this idea offers the highest probability of strong demo and judging alignment")
    disclaimer: str = Field(
        default="No win is guaranteed. Scoring reflects alignment with feasibility, innovation, and demo polish.",
        description="Mandatory disclaimer"
    )


# ---------------------------------------------------------------------------
# Feature 5: MVP Planner Schemas
# ---------------------------------------------------------------------------

class MVPPlanResponse(BaseModel):
    """MoSCoW prioritized feature list optimized for a working hackathon prototype."""
    project_title: str
    core_mvp_summary: str
    must_have_features: List[str] = Field(..., description="Absolute bare minimum needed for a functioning demo")
    should_have_features: List[str] = Field(..., description="High-value features to add if time permits")
    nice_to_have_features: List[str] = Field(..., description="Features to intentionally cut/defer to post-hackathon")
    minimal_demo_flow: List[str] = Field(..., description="The exact 3-step user flow demonstrated to judges")
    potential_failure_points: List[str] = Field(..., description="Things that could break during live presentation and how to bypass them")


# ---------------------------------------------------------------------------
# Feature 6: Time-Boxed Roadmap Schemas
# ---------------------------------------------------------------------------

class RoadmapTimeBlock(BaseModel):
    time_window: str = Field(..., description="E.g. 'Hours 0-4' or 'Hours 18-22'")
    focus_milestone: str = Field(..., description="Primary milestone (e.g. 'Architecture & Ingestion Worker')")
    frontend_tasks: List[str]
    backend_ai_tasks: List[str]
    integration_and_testing: List[str]
    deliverable: str


class HackathonRoadmapResponse(BaseModel):
    """Time-budgeted roadmap covering ideation to presentation."""
    hackathon_duration: str
    total_hours: int
    time_blocks: List[RoadmapTimeBlock]
    reserved_buffer_hours: float = Field(..., description="Hours intentionally reserved for integration, debugging, and demo polish")
    submission_checklist: List[str]


# ---------------------------------------------------------------------------
# Feature 7: Team Allocation Schemas
# ---------------------------------------------------------------------------

class MemberAssignment(BaseModel):
    member_identifier: str = Field(..., description="E.g. 'Member 1 (Frontend Lead)'")
    assigned_role: str
    key_responsibilities: List[str]
    specific_tasks: List[str]
    expected_deliverables: List[str]


class TeamAllocationResponse(BaseModel):
    """Team task distribution based on individual and group skills."""
    project_title: str
    team_size: int
    member_assignments: List[MemberAssignment]
    coordination_practices: List[str] = Field(..., description="Quick tips for git branching, mock APIs, and standups")


# ---------------------------------------------------------------------------
# Features 8 & 9: Free-First Tech & Development Guidance Schemas
# ---------------------------------------------------------------------------

class TechTierItem(BaseModel):
    tech_name: str
    category: str
    license_type: str = Field(..., description="'Free', 'Open-Source', 'Freemium', or 'Paid'")
    why_recommended: str
    free_tier_limits: str = Field(..., description="Exact free-tier quotas (e.g. 100k requests/month, 500MB DB)")
    free_alternative: Optional[str] = Field(default=None, description="Fallback if limits are exceeded")


class HackathonDevGuidanceResponse(BaseModel):
    """Fast-track development guide for the chosen hackathon MVP."""
    project_title: str
    recommended_tech_stack: List[TechTierItem]
    database_design_summary: str
    suggested_api_endpoints: List[str]
    integration_quickstart_guide: List[str]
    copy_ready_claude_prompt: str
    copy_ready_antigravity_prompt: str
    testing_and_sanity_checks: List[str]
    deployment_plan: str


# ---------------------------------------------------------------------------
# Feature 10: Pitch and Demo Preparation Schemas
# ---------------------------------------------------------------------------

class JudgeQAItem(BaseModel):
    anticipated_question: str
    suggested_answer: str
    highlight_aspect: str = Field(..., description="Which strength to emphasize (e.g. Feasibility, Scalability)")


class PitchAndDemoResponse(BaseModel):
    """Multi-duration pitch scripts, live demo walkthrough, and judge defense."""
    project_title: str
    pitch_30_seconds: str = Field(..., description="Punchy 30-second elevator pitch / opening hook")
    pitch_1_minute: str = Field(..., description="1-minute problem-solution overview")
    pitch_3_minute: str = Field(..., description="3-minute standard hackathon presentation script with timing markers")
    pitch_5_minute: str = Field(..., description="5-minute comprehensive presentation script with deep tech explanation")
    live_demo_walkthrough: List[str] = Field(..., description="Step-by-step 2-minute live demo sequence")
    technical_explanation: str = Field(..., description="Clear explanation of the architecture and algorithms for technical judges")
    innovation_explanation: str = Field(..., description="Explicit highlight of the novel contribution")
    judge_qa_preparation: List[JudgeQAItem]
    future_scope: List[str] = Field(..., description="Realistic post-hackathon roadmap items")


# ---------------------------------------------------------------------------
# Master Hackathon Strategy Schema
# ---------------------------------------------------------------------------

class FullHackathonStrategyResponse(BaseModel):
    """Unified master hackathon strategy bundle."""
    hackathon_name: str
    duration: str
    analysis: HackathonAnalysisResponse
    ideas: HackathonIdeasResponse
    evaluation: IdeaEvaluationResponse
    mvp_plan: MVPPlanResponse
    roadmap: HackathonRoadmapResponse
    team_allocation: TeamAllocationResponse
    development_guidance: HackathonDevGuidanceResponse
    pitch_and_demo: PitchAndDemoResponse
    metadata: Dict[str, Any] = Field(default_factory=dict)
