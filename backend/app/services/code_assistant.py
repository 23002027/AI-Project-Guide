"""
Coding Assistant Service (Phase 9).

Provides module starter code generation, debugging and traceback analysis,
and unit test scaffolding using Claude.
Separates generated code from explanations and never automatically executes untrusted code.
"""

from typing import Optional
from backend.app.schemas.coding_assistant import (
    CodeGenerateRequest,
    CodeGenerateResponse,
    CodeDebugRequest,
    CodeDebugResponse,
)
from backend.app.services.claude_service import ClaudeService


class CodeAssistantService:
    """Intelligent coding and debugging service."""

    def __init__(self, claude_service: Optional[ClaudeService] = None):
        self.claude = claude_service or ClaudeService()

    async def generate_starter_code(self, req: CodeGenerateRequest) -> CodeGenerateResponse:
        """Generate production-ready starter code with unit tests and clear explanation."""
        system_prompt = """You are a Principal Software Engineer and Technical Mentor.
Generate clean, production-grade starter code for college engineering projects.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object strictly matching the schema.
2. Provide real, working, robust code. Do not use vague placeholders or '// implement here'.
3. Include input validation, type hints, error handling, and docstrings.
4. Clearly separate the executable code from the explanation.
5. Provide a matching unit test scaffold using pytest (for Python) or Jest/Vitest (for JS/TS)."""

        user_prompt = f"""Generate starter code for module:
- Module Name: {req.module_name}
- Language: {req.language}
- Framework: {req.framework or 'Standard'}
- Description: {req.description}
- Project Context: {req.project_context or 'College Capstone / Hackathon Project'}

Return valid JSON adhering to CodeGenerateResponse schema."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=CodeGenerateResponse,
            max_tokens=4096,
        )

    async def debug_code(self, req: CodeDebugRequest) -> CodeDebugResponse:
        """Analyze code snippets and tracebacks to find the root cause and provide a drop-in fix."""
        system_prompt = """You are an Expert Debugger and Senior Systems Architect.
Analyze the provided code snippet, error traceback, and expected behavior.

CRITICAL INSTRUCTIONS:
1. Respond ONLY with a single valid JSON object strictly matching the schema.
2. Accurately identify the root cause of the error.
3. Provide a complete, drop-in replacement code snippet that fixes the bug.
4. Explain why the bug occurred and how the fix resolves it.
5. Provide preventive advice for similar bugs."""

        user_prompt = f"""Debug the following code:
- Language: {req.language}
- Expected Behavior: {req.expected_behavior or 'Execute without exceptions'}
- Error Traceback:
```
{req.error_traceback or 'No traceback provided (logical bug or silent failure)'}
```

- Code Snippet:
```{req.language}
{req.code_snippet}
```

Return valid JSON adhering to CodeDebugResponse schema."""

        return await self.claude.complete_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=CodeDebugResponse,
            max_tokens=4096,
        )
