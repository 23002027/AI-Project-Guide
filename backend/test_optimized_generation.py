import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import json
import time
from backend.app.schemas.project_guidance import (
    ProjectAnalysisResponse,
    ProjectIdeaInput,
    ProjectDomain,
    ExperienceLevel
)

def run_test():
    payload = ProjectIdeaInput(
        title="AI Healthcare Triage Assistant",
        description="Automated triage and preliminary diagnostic guidance for rural healthcare clinics using machine learning and NLP.",
        domain=ProjectDomain.HEALTHCARE,
        skills=["Python", "FastAPI", "React"],
        experience_level=ExperienceLevel.INTERMEDIATE,
        deadline="3 months",
        is_team=True,
        team_size=3,
        budget="Free Tier"
    )

    system_prompt = (
        "You are an expert technical advisor for university engineering projects. "
        "Provide a concise, high-quality project analysis. "
        "Output ONLY a valid JSON object matching the requested schema. No conversational filler."
    )

    user_prompt = f"""Analyze the following engineering project and provide a JSON response:
Project Title: {payload.title}
Domain: {payload.domain.value}
Description: {payload.description}
Team Skills: {', '.join(payload.skills)}
Deadline: {payload.deadline}
Team Size: {payload.team_size} members

The JSON object must have exactly these keys:
- "project_title": string
- "domain": string
- "problem_statement": string (1-2 sentences)
- "existing_limitations": list of 2 concise strings
- "proposed_solution": string (1-2 sentences)
- "target_users": list of 2 concise strings
- "main_objectives": list of 2 concise strings
- "expected_outcomes": list of 2 concise strings
- "unique_selling_proposition": string (1 sentence)
- "innovation_opportunities": list of 2 concise strings
- "feasibility_assessment": string (1-2 sentences)
- "project_complexity": "Moderate" or "High" or "Advanced"
- "follow_up_questions": list of 2 concise strings
"""

    req_body = {
        "model": "qwen3:4b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "format": "json",
        "think": False,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 1200
        }
    }

    print(">>> Starting optimized Ollama generation test...", flush=True)
    print(f">>> Target model: {req_body['model']}, think: {req_body['think']}, format: {req_body['format']}", flush=True)
    t0 = time.time()

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(req_body).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        resp = urllib.request.urlopen(req, timeout=180)
        raw_resp = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - t0

        raw_content = raw_resp.get("message", {}).get("content", "")
        eval_count = raw_resp.get("eval_count", 0)
        prompt_eval_count = raw_resp.get("prompt_eval_count", 0)
        done_reason = raw_resp.get("done_reason", "unknown")

        print(f">>> [SUCCESS] HTTP response received in {elapsed:.2f} seconds!")
        print(f">>> Prompt Tokens Evaluated: {prompt_eval_count}")
        print(f">>> Output Tokens Generated: {eval_count}")
        print(f">>> Done Reason: {done_reason}")
        print(f">>> Generation Speed: {eval_count / elapsed:.2f} tokens/second" if elapsed > 0 else "")

        # Parse JSON
        data = json.loads(raw_content.strip())

        # Pydantic schema validation
        validated = ProjectAnalysisResponse.model_validate(data)
        print(">>> [PYDANTIC VALIDATION]: PASSED")
        print("\n--- Validated Content Summary ---")
        print(f"Project Title: {validated.project_title}")
        print(f"Domain: {validated.domain}")
        print(f"Problem Statement: {validated.problem_statement}")
        print(f"Proposed Solution: {validated.proposed_solution}")
        print(f"USP: {validated.unique_selling_proposition}")
        print(f"Complexity: {validated.project_complexity}")
        print(f"Feasibility: {validated.feasibility_assessment}")
        print(f"Objectives ({len(validated.main_objectives)}): {validated.main_objectives}")
        print(f"Target Users ({len(validated.target_users)}): {validated.target_users}")
        print(f"Limitations ({len(validated.existing_limitations)}): {validated.existing_limitations}")
        print(f"Expected Outcomes ({len(validated.expected_outcomes)}): {validated.expected_outcomes}")
        print(f"Innovation Opportunities ({len(validated.innovation_opportunities)}): {validated.innovation_opportunities}")
        print(f"Follow-up Questions ({len(validated.follow_up_questions)}): {validated.follow_up_questions}")

    except urllib.error.HTTPError as e:
        print(f">>> [ERROR] HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f">>> [ERROR] Connection / Timeout: {e}")
    except json.JSONDecodeError as e:
        print(f">>> [ERROR] JSON Decode Error: {e}")
        print("Raw Content was:", raw_content[:500])
    except Exception as e:
        print(f">>> [ERROR]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
