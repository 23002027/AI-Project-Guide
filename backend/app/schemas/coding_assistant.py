"""
Pydantic Schemas for Coding Assistance & GitHub Integration (Phase 9).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CodeGenerateRequest(BaseModel):
    module_name: str = Field(..., min_length=2, description="Name of module or component")
    language: str = Field(default="python", description="Programming language (python, typescript, etc.)")
    framework: Optional[str] = Field(default="FastAPI", description="Framework or library")
    description: str = Field(..., min_length=10, description="What this code should do")
    project_context: Optional[str] = Field(default="", description="High-level project background")


class CodeGenerateResponse(BaseModel):
    module_name: str
    language: str
    file_path: str = Field(..., description="Recommended file location (e.g. backend/app/services/worker.py)")
    starter_code: str = Field(..., description="Production-ready starter code")
    implementation_steps: List[str] = Field(..., description="Step-by-step guidance to wire this module")
    code_explanation: str = Field(..., description="Clear explanation of how the code works")
    unit_test_code: str = Field(..., description="Complete unit test scaffold for this module")
    security_tips: List[str] = Field(default_factory=list, description="Security and error handling tips")


class CodeDebugRequest(BaseModel):
    code_snippet: str = Field(..., min_length=5, description="Code containing bug or error")
    error_traceback: Optional[str] = Field(default="", description="Stack trace or error message")
    language: str = Field(default="python", description="Programming language")
    expected_behavior: Optional[str] = Field(default="", description="What the code was supposed to do")


class CodeDebugResponse(BaseModel):
    error_analysis: str = Field(..., description="Diagnosis of the bug or exception")
    root_cause: str = Field(..., description="Why the error occurred")
    suggested_fix_code: str = Field(..., description="Corrected drop-in replacement code")
    explanation: str = Field(..., description="Detailed explanation of the fix")
    prevention_advice: List[str] = Field(default_factory=list, description="How to avoid similar bugs")


class GitHubScaffoldRequest(BaseModel):
    repo_name: str = Field(default="ai-project-copilot", description="Repository name")
    project_title: str = Field(..., description="Full project title")
    description: str = Field(..., description="Project summary")
    tech_stack: List[str] = Field(default_factory=lambda: ["Python", "FastAPI", "React"], description="Key technologies")
    is_private: bool = Field(default=False)


class GitHubIssueTemplate(BaseModel):
    title: str
    labels: List[str]
    body: str


class GitHubScaffoldResponse(BaseModel):
    repo_name: str
    github_configured: bool
    readme_content: str = Field(..., description="Professional GitHub README.md with badges and architecture")
    suggested_gitignore: str = Field(..., description="Language-specific .gitignore rules")
    suggested_directory_tree: str = Field(..., description="ASCII directory layout")
    suggested_issues: List[GitHubIssueTemplate] = Field(default_factory=list, description="Milestone tasks formatted as GitHub issues")
    setup_commands: List[str] = Field(default_factory=list, description="Git commands to initialize repository")
