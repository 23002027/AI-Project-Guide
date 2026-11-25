"""
Supervisor: rule-based Python router.

Reads `workflow_type` from the shared state and returns the ordered list of
agent node names LangGraph should execute.  Using deterministic Python logic
(instead of an LLM call) means zero extra AI-credit cost for routing.
"""

from __future__ import annotations

from typing import List


# Map each workflow type to an ordered sequence of agent node names.
WORKFLOW_CHAINS: dict[str, List[str]] = {
    # Core project analysis and plan
    "project": [
        "project_analyzer",
        "technology_advisor",
        "architecture",
        "roadmap",
    ],
    # Full end-to-end 7-agent project guidance
    "full_project": [
        "project_analyzer",
        "technology_advisor",
        "architecture",
        "roadmap",
        "coding",
        "documentation",
        "testing",
    ],
    # Complete 7-agent hackathon guidance
    "hackathon": [
        "hackathon_analyzer",
        "idea_generator",
        "idea_evaluation",
        "mvp_planning",
        "team_allocation",
        "dev_guidance",
        "pitch",
    ],
    # Full hackathon co-pilot run
    "full_hackathon": [
        "hackathon_analyzer",
        "idea_generator",
        "idea_evaluation",
        "mvp_planning",
        "team_allocation",
        "dev_guidance",
        "pitch",
    ],
}

# Agents that require explicit user approval before execution
APPROVAL_REQUIRED_AGENTS: set[str] = {
    "architecture",   # changes high-level design
    "roadmap",        # commits to a development timeline
    "mvp_planning",   # scopes project boundary
}


def get_agent_chain(workflow_type: str) -> List[str]:
    """Return the ordered agent chain for a given workflow type."""
    return WORKFLOW_CHAINS.get(workflow_type, WORKFLOW_CHAINS["project"])


def requires_approval(agent_name: str) -> bool:
    """Return True if the agent needs user confirmation before running."""
    return agent_name in APPROVAL_REQUIRED_AGENTS
