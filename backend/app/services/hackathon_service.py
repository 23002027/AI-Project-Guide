"""
Hackathon Guidance Service (Phase 4).
Specialized intelligence layer for hackathon problem analysis,
multi-idea brainstorming, weighted idea evaluation, MVP scoping,
time-boxed hourly sprint planning, team allocation, and multi-tier pitch decks.
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Optional, List

from backend.app.schemas.hackathon_guidance import (
    HackathonInput,
    HackathonAnalysisResponse,
    HackathonIdeaItem,
    HackathonIdeasResponse,
    IdeaEvaluationResponse,
    MVPPlanResponse,
    HackathonRoadmapResponse,
    TeamAllocationResponse,
    HackathonDevGuidanceResponse,
    PitchAndDemoResponse,
    FullHackathonStrategyResponse,
)
from backend.app.services.claude_service import ClaudeService


class HackathonService:
    """Orchestration service for hackathon guidance workflows."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    # -----------------------------------------------------------------------
    # Feature 2: Problem Statement Analyzer
    # -----------------------------------------------------------------------
    async def analyze_problem(self, req: HackathonInput) -> HackathonAnalysisResponse:
        system_prompt = """You are a Veteran Hackathon Mentor and Judging Committee Advisor.
Analyze the provided hackathon problem statement to extract actionable insights for a competitive hackathon team.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Identify core requirements versus superficial problem descriptions.
3. Highlight high-impact innovation angles that catch judges' attention in under 3 minutes."""

        schema_sample = {
            "hackathon_name": req.hackathon_name,
            "problem_summary": "Concise summary of the core issue...",
            "target_users": ["User Persona 1", "User Persona 2"],
            "existing_challenges": ["Challenge 1", "Challenge 2"],
            "core_requirements": ["Requirement 1", "Requirement 2"],
            "expected_solution": "Characteristics of an ideal winning prototype...",
            "constraints": ["Time constraint of " + req.duration, "Resource constraints..."],
            "potential_opportunities": ["Opportunity 1", "Opportunity 2"]
        }

        user_prompt = f"""Analyze this hackathon problem statement:
- Hackathon: {req.hackathon_name}
- Problem Statement: {req.problem_statement}
- Track / Domain: {req.domain or 'General'}
- Available Duration: {req.duration}
- Team Size: {req.team_size}
- Team Skills: {', '.join(req.team_skills)}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=HackathonAnalysisResponse,
            max_tokens=4096
        )




    # -----------------------------------------------------------------------
    # Feature 3: Hackathon Idea Generator (At least 5 distinct ideas)
    # -----------------------------------------------------------------------
    async def generate_ideas(self, req: HackathonInput) -> HackathonIdeasResponse:
        system_prompt = """You are an Elite Hackathon Strategist.
Your goal is to generate at least 5 GENUINELY DIFFERENT, innovative, and viable project concepts for this hackathon.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object matching the schema.
2. Generate AT LEAST 5 distinct ideas. Avoid minor variations of the same idea.
   - Idea 1: Direct, high-polish MVP approach.
   - Idea 2: Novel AI/Agentic automation approach.
   - Idea 3: Edge / Lightweight offline-first approach.
   - Idea 4: Data-driven predictive or aggregation approach.
   - Idea 5: Workflow or collaborative platform approach.
3. Every idea must be technically feasible within the team's available duration and stated skills."""

        schema_sample = {
            "hackathon_name": req.hackathon_name,
            "ideas": [
                {
                    "idea_id": 1,
                    "project_title": "Distinct Project Concept 1",
                    "problem_solved": "Specific problem addressed...",
                    "proposed_solution": "Concrete technical solution...",
                    "innovation_angle": "What makes this stand out to judges...",
                    "key_features": ["Feature A", "Feature B", "Feature C"],
                    "suggested_tech_stack": ["FastAPI", "React"],
                    "technical_feasibility": "High",
                    "expected_impact": "Direct operational impact...",
                    "demo_potential": "High (Instant visual feedback on dashboard)"
                }
            ]
        }

        user_prompt = f"""Brainstorm 5 genuinely distinct, highly competitive hackathon ideas:
- Problem: {req.problem_statement}
- Duration: {req.duration}
- Team Size: {req.team_size} members
- Skills: {', '.join(req.team_skills)}
- Experience: {req.experience_level}
- Budget: {req.budget or 'Free Tier'}

EXPECTED JSON SCHEMA (Must contain 5+ ideas in the 'ideas' array):
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON with at least 5 distinct ideas."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=HackathonIdeasResponse,
            max_tokens=4096
        )

    # -----------------------------------------------------------------------
    # Feature 4: Idea Evaluation & Scoring
    # -----------------------------------------------------------------------
    async def evaluate_ideas(
        self,
        req: HackathonInput,
        ideas: Optional[List[HackathonIdeaItem]] = None
    ) -> IdeaEvaluationResponse:
        # If ideas not explicitly passed, check payload or generate them
        if not ideas and req.candidate_ideas:
            ideas = req.candidate_ideas
        if not ideas:
            gen_result = await self.generate_ideas(req)
            ideas = gen_result.ideas

        system_prompt = """You are a Chief Hackathon Judge.
Evaluate and score the provided hackathon concepts objectively across standard criteria.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Score each idea from 0 to 10 on:
   - Problem Relevance (Weight 20%)
   - Innovation (Weight 20%)
   - Technical Feasibility (Weight 20%)
   - Social / Business Impact (Weight 15%)
   - Demo Potential (Weight 15%)
   - Time Feasibility (Weight 10%)
   (If official judging criteria were provided in the prompt, adapt weights accordingly).
3. Compute weighted_total_score on a scale of 0 to 10.
4. Recommend the single strongest idea and justify why it provides the highest chance of judging impact.
5. NEVER guarantee a win; emphasize execution and presentation polish."""

        ideas_summary = [
            {
                "idea_id": i.idea_id,
                "project_title": i.project_title,
                "proposed_solution": i.proposed_solution,
                "tech_stack": i.suggested_tech_stack,
                "demo_potential": i.demo_potential
            }
            for i in ideas
        ]

        schema_sample = {
            "scoring_method": "Default Balanced Matrix (Relevance 20%, Innovation 20%, Feasibility 20%, Impact 15%, Demo 15%, Time 10%)",
            "ranked_ideas": [
                {
                    "idea_id": 1,
                    "project_title": "Project Title 1",
                    "problem_relevance": 9.0,
                    "innovation": 8.5,
                    "technical_feasibility": 9.0,
                    "social_business_impact": 8.0,
                    "demo_potential": 9.5,
                    "time_feasibility": 8.5,
                    "weighted_total_score": 8.75,
                    "strengths": ["Instant visual appeal", "Realistic scope"],
                    "risks_and_pitfalls": ["Avoid getting bogged down in authentication"]
                }
            ],
            "recommended_idea_id": 1,
            "recommended_idea_title": "Project Title 1",
            "recommendation_rationale": "Highest combination of demo polish and reliable completion within the deadline.",
            "disclaimer": "No win is guaranteed. Scoring reflects alignment with feasibility, innovation, and demo polish."
        }

        user_prompt = f"""Evaluate these {len(ideas)} ideas for the hackathon:
- Duration: {req.duration}
- Team Skills: {', '.join(req.team_skills)}
- Team Size: {req.team_size}
- Official Judging Rules/Criteria: {json.dumps([c.model_dump() for c in req.judging_criteria]) if req.judging_criteria else 'None specified (use default matrix)'}

CANDIDATE IDEAS:
{json.dumps(ideas_summary, indent=2)}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=IdeaEvaluationResponse,
            max_tokens=4096
        )

    # -----------------------------------------------------------------------
    # Feature 5: MVP Planner
    # -----------------------------------------------------------------------
    async def plan_mvp(
        self,
        req: HackathonInput,
        selected_title: Optional[str] = None
    ) -> MVPPlanResponse:
        system_prompt = """You are a Lean Startup MVP Architect and Hackathon Veteran.
Your task is to ruthlessly scope the project into Must-Have, Should-Have, and Nice-to-Have (MoSCoW) features.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. In hackathons, teams lose by trying to build too much. Prioritize a single, robust, end-to-end working flow over 10 half-built features.
3. Identify exactly which features to CUT or DEFER (Nice-to-Have).
4. Outline a 3-step minimal demo flow and prepare failure mitigations for when live APIs or Wi-Fi glitch."""

        schema_sample = {
            "project_title": selected_title or "Selected Hackathon Project",
            "core_mvp_summary": "A razor-focused prototype delivering the core value loop...",
            "must_have_features": [
                "Feature 1: Core input interface",
                "Feature 2: Real-time processing pipeline",
                "Feature 3: Output visualization card"
            ],
            "should_have_features": [
                "Feature 4: Filterable metrics table"
            ],
            "nice_to_have_features": [
                "Complex authentication (use role dropdown instead)",
                "Payment gateway integration (defer)",
                "Full mobile app build (use responsive web instead)"
            ],
            "minimal_demo_flow": [
                "Step 1: Present sample input data",
                "Step 2: Trigger AI processing live",
                "Step 3: Show immediate resulting analytics"
            ],
            "potential_failure_points": [
                "External API rate limits -> Pre-cache 3 sample responses locally",
                "Wi-Fi latency -> Run local Uvicorn instance on localhost"
            ]
        }

        user_prompt = f"""Create an MVP MoSCoW plan for:
- Title / Focus: {selected_title or req.problem_statement[:80]}
- Problem: {req.problem_statement}
- Duration: {req.duration}
- Team Size: {req.team_size} members
- Skills: {', '.join(req.team_skills)}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MVPPlanResponse,
            max_tokens=4096
        )




    # -----------------------------------------------------------------------
    # Feature 6: Time-Boxed Roadmap
    # -----------------------------------------------------------------------
    async def generate_roadmap(self, req: HackathonInput) -> HackathonRoadmapResponse:
        system_prompt = """You are an Agile Sprint Master for Hackathons.
Generate a realistic, time-boxed hourly development schedule calibrated precisely to the hackathon's duration.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Break the timeline into balanced time blocks matching the hackathon duration (e.g. 24h, 36h, 48h).
3. MANDATORY: Explicitly reserve at least 20-25% of total time at the end for Integration, Testing, Pitch Preparation, and Live Demo Rehearsal.
4. Include parallel tracks for Frontend and Backend/AI to prevent team bottlenecks."""

        schema_sample = {
            "hackathon_duration": req.duration,
            "total_hours": 24,
            "time_blocks": [
                {
                    "time_window": "Hours 0 - 3",
                    "focus_milestone": "Architecture, Repo Setup & Mock Contracts",
                    "frontend_tasks": ["Initialize Vite + React, setup UI layout"],
                    "backend_ai_tasks": ["Initialize FastAPI, write mock endpoints"],
                    "integration_and_testing": ["Verify CORS and dummy API response"],
                    "deliverable": "Working client-server handshake with mock data"
                },
                {
                    "time_window": "Hours 3 - 10",
                    "focus_milestone": "Core Pipeline & UI Feature Development",
                    "frontend_tasks": ["Build input forms and result visualizer"],
                    "backend_ai_tasks": ["Integrate core AI model/algorithm"],
                    "integration_and_testing": ["Unit test core business logic"],
                    "deliverable": "End-to-end data processing functioning"
                },
                {
                    "time_window": "Hours 10 - 18",
                    "focus_milestone": "Full Integration & Polish",
                    "frontend_tasks": ["Error states, toast notifications, loading spinners"],
                    "backend_ai_tasks": ["Performance optimization, caching"],
                    "integration_and_testing": ["End-to-end integration testing"],
                    "deliverable": "Feature-complete MVP ready for demo lockdown"
                },
                {
                    "time_window": "Hours 18 - 24 (CRITICAL BUFFER)",
                    "focus_milestone": "Code Freeze, Pitch Deck & Live Demo Rehearsals",
                    "frontend_tasks": ["Freeze code, UI polish only"],
                    "backend_ai_tasks": ["Local fallback data seeding"],
                    "integration_and_testing": ["Dry-run presentation 3 times with stopwatch"],
                    "deliverable": "Final slide deck, recorded backup video, and rehearsed live demo"
                }
            ],
            "reserved_buffer_hours": 6.0,
            "submission_checklist": [
                "GitHub repository made public with informative README",
                "2-minute demo video recorded and uploaded as backup",
                "Devpost / Portal form submitted at least 30 minutes before deadline"
            ]
        }

        user_prompt = f"""Generate a time-boxed roadmap for:
- Hackathon Duration: {req.duration}
- Team Size: {req.team_size} members
- Skills: {', '.join(req.team_skills)}
- Problem Statement: {req.problem_statement[:150]}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON matching the exact total hours of '{req.duration}'."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=HackathonRoadmapResponse,
            max_tokens=4096
        )




    # -----------------------------------------------------------------------
    # Feature 7: Team Allocation
    # -----------------------------------------------------------------------
    async def allocate_team(self, req: HackathonInput) -> TeamAllocationResponse:
        system_prompt = """You are a Technical Team Lead for Hackathons.
Assign clear, balanced responsibilities to each team member based on team size and skills, preventing idle time and parallelizing delivery.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Provide exactly one assignment per team member (matching `team_size`).
3. Ensure one member is explicitly designated as the Pitch & Demo Owner to prevent last-minute presentation panic."""

        members_info = ""
        if req.team_members:
            members_info = "\nINDIVIDUAL MEMBERS:\n" + "\n".join(
                [f"- {m.member_name} (Prefers: {m.role_preference or 'Any'}, Skills: {', '.join(m.skills)})" for m in req.team_members]
            )

        schema_sample = {
            "project_title": req.hackathon_name,
            "team_size": req.team_size,
            "member_assignments": [
                {
                    "member_identifier": "Member 1 (Frontend & UI Lead)",
                    "assigned_role": "Frontend Architect",
                    "key_responsibilities": ["React dashboard", "Responsive design", "State management"],
                    "specific_tasks": ["Setup Vite/Tailwind", "Connect API calls", "Polish animations"],
                    "expected_deliverables": ["Interactive UI running with mock & live API"]
                }
            ],
            "coordination_practices": [
                "Use Git feature branches; never push broken code directly to main",
                "Agree on JSON API schemas in Hour 1 so Frontend and Backend work in parallel",
                "Conduct 5-minute sync standups every 4 hours"
            ]
        }

        user_prompt = f"""Allocate responsibilities for this hackathon team:
- Team Size: {req.team_size} member(s)
- Aggregated Skills: {', '.join(req.team_skills)}
- Experience Level: {req.experience_level}
- Duration: {req.duration}
{members_info}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON with exactly {req.team_size} member assignments."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=TeamAllocationResponse,
            max_tokens=4096
        )




    # -----------------------------------------------------------------------
    # Features 8 & 9: Free-First Tech & Dev Guidance
    # -----------------------------------------------------------------------
    async def generate_dev_guidance(
        self,
        req: HackathonInput,
        selected_title: Optional[str] = None
    ) -> HackathonDevGuidanceResponse:
        system_prompt = """You are a Practical Full-Stack AI Engineer.
Recommend a FREE-FIRST technology stack and rapid integration playbook for a hackathon.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Prioritize 100% Free and Open-Source tools by default.
3. Clearly classify each tool as 'Free', 'Open-Source', 'Freemium', or 'Paid'.
4. Include copy-ready prompts for Claude and Antigravity that incorporate actual project details."""

        schema_sample = {
            "project_title": selected_title or "Hackathon Project",
            "recommended_tech_stack": [
                {
                    "tech_name": "FastAPI",
                    "category": "Backend Framework",
                    "license_type": "Open-Source",
                    "why_recommended": "Fastest async framework with auto-generated Swagger UI for instant testing",
                    "free_tier_limits": "100% Free / Self-hosted",
                    "free_alternative": "Flask"
                },
                {
                    "tech_name": "Vercel / Render",
                    "category": "Cloud Hosting",
                    "license_type": "Freemium",
                    "why_recommended": "Zero-config deployment from GitHub repository",
                    "free_tier_limits": "Free Hobby Tier with generous bandwidth",
                    "free_alternative": "Localhost ngrok tunnel"
                }
            ],
            "database_design_summary": "Minimal schema: SQLite / Neon Postgres with tables for Inputs, Results, and Feedback.",
            "suggested_api_endpoints": [
                "POST /api/process (Core AI processing)",
                "GET /api/results (Fetch historical results)"
            ],
            "integration_quickstart_guide": [
                "1. Setup backend and enable CORS for http://localhost:3000",
                "2. Create Axios client in React frontend with base URL pointing to FastAPI"
            ],
            "copy_ready_claude_prompt": f"Act as a Senior Python Engineer. I am participating in '{req.hackathon_name}' with a deadline of '{req.duration}'. Write a complete FastAPI route with Pydantic validation that...",
            "copy_ready_antigravity_prompt": f"Scaffold an end-to-end hackathon MVP for '{req.hackathon_name}' with a React frontend and FastAPI backend. Prioritize clean visual appeal and error fallback...",
            "testing_and_sanity_checks": [
                "Test API with curl or Swagger before connecting UI",
                "Verify demo works with network disconnected using cached mock data"
            ],
            "deployment_plan": "Deploy frontend to Vercel and backend to Render free tier, with a local ngrok tunnel as live backup."
        }

        user_prompt = f"""Generate free-first tech and development guidance for:
- Title: {selected_title or req.problem_statement[:80]}
- Problem: {req.problem_statement}
- Duration: {req.duration}
- Skills: {', '.join(req.team_skills)}
- Budget: {req.budget or 'Free Tier'}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=HackathonDevGuidanceResponse,
            max_tokens=4096
        )

    # Alias for agent orchestrator compatibility
    advise_technologies = generate_dev_guidance




    # -----------------------------------------------------------------------
    # Feature 10: Pitch & Demo Preparation
    # -----------------------------------------------------------------------
    async def generate_pitch(
        self,
        req: HackathonInput,
        selected_title: Optional[str] = None
    ) -> PitchAndDemoResponse:
        system_prompt = """You are a World-Class Hackathon Pitch Coach.
Create multi-duration pitch scripts, a live demo walkthrough, and judge defense Q&A.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object adhering strictly to the schema.
2. Provide pitches tailored to 4 standard formats: 30 seconds, 1 minute, 3 minutes, and 5 minutes.
3. The live demo sequence must be a crisp 2-minute chronological walkthrough (Hook -> Problem in action -> Solution -> Tech under the hood -> Business Impact).
4. Anticipate tough technical judge questions (Scalability, Accuracy, Edge cases, API latency) with persuasive, honest answers.
5. Never invent false experimental results or claim unfinished features are operational."""

        schema_sample = {
            "project_title": selected_title or "Hackathon Project",
            "pitch_30_seconds": "Imagine if... [Punchy hook, core problem, our solution, and immediate impact].",
            "pitch_1_minute": "Every day, thousands of... [Problem context]. That's why we built... [Solution and 1 key metric]. Thank you.",
            "pitch_3_minute": "0:00-0:30: The Hook & Problem...\n0:30-1:30: Live Demonstration walkthrough...\n1:30-2:15: Tech Stack & Architecture...\n2:15-3:00: Business Viability & Future Scope.",
            "pitch_5_minute": "Comprehensive 5-minute pitch script including deep-dive on architecture, design decisions, and live demo markers...",
            "live_demo_walkthrough": [
                "1. Open dashboard; point to realistic sample input",
                "2. Click 'Execute'; show real-time processing under 1 second",
                "3. Highlight the primary innovative insight on the results screen"
            ],
            "technical_explanation": "Explain algorithms, data flow, and architectural decisions clearly for engineer judges...",
            "innovation_explanation": "Clearly articulate why this approach is 10x better than existing solutions...",
            "judge_qa_preparation": [
                {
                    "anticipated_question": "How will this handle scale if 10,000 users query it simultaneously?",
                    "suggested_answer": "Our FastAPI backend is stateless and decoupled from the AI inference worker via an async queue, allowing horizontal container scaling on AWS/Render.",
                    "highlight_aspect": "Architectural Scalability"
                }
            ],
            "future_scope": [
                "Post-hackathon mobile app deployment",
                "Integration with real-time enterprise webhook APIs"
            ]
        }

        user_prompt = f"""Create complete pitch and demo preparation materials for:
- Title: {selected_title or req.problem_statement[:80]}
- Problem Statement: {req.problem_statement}
- Duration: {req.duration}
- Skills: {', '.join(req.team_skills)}

EXPECTED JSON SCHEMA:
{json.dumps(schema_sample, indent=2)}

Return ONLY valid JSON."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=PitchAndDemoResponse,
            max_tokens=4096
        )




    # -----------------------------------------------------------------------
    # Master Strategy Pipeline (Coordinates all modules concurrently)
    # -----------------------------------------------------------------------
    async def generate_full_strategy(self, req: HackathonInput) -> FullHackathonStrategyResponse:
        """Executes all hackathon guidance dimensions concurrently via asyncio.gather."""
        # 1. First get ideas & analysis
        analysis, ideas_resp = await asyncio.gather(
            self.analyze_problem(req),
            self.generate_ideas(req),
        )

        # 2. Evaluate ideas
        eval_resp = await self.evaluate_ideas(req, ideas_resp.ideas)
        best_title = eval_resp.recommended_idea_title

        # 3. Concurrently generate MVP, roadmap, team allocation, dev guide, and pitch
        mvp, roadmap, team, dev_guide, pitch = await asyncio.gather(
            self.plan_mvp(req, best_title),
            self.generate_roadmap(req),
            self.allocate_team(req),
            self.generate_dev_guidance(req, best_title),
            self.generate_pitch(req, best_title),
        )

        return FullHackathonStrategyResponse(
            hackathon_name=req.hackathon_name,
            duration=req.duration,
            analysis=analysis,
            ideas=ideas_resp,
            evaluation=eval_resp,
            mvp_plan=mvp,
            roadmap=roadmap,
            team_allocation=team,
            development_guidance=dev_guide,
            pitch_and_demo=pitch,
            metadata={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "duration": req.duration,
                "team_size": req.team_size
            }
        )
