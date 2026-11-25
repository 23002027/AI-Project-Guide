import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("=" * 60)
print("TESTING EXPORT ENDPOINTS & APPLICATION RESTART")
print("=" * 60)

# 1. Test POST /api/presentation/generate-pptx
pptx_payload = {
    "title": "Smart Campus Energy Management",
    "domain": "IoT & Smart Devices",
    "author": "Engineering Team",
    "institution": "National Institute of Technology",
    "analysis": {
        "problem_statement": "High campus energy waste due to unmonitored facilities.",
        "proposed_solution": "IoT-based real-time load distribution system."
    },
    "technology_stack": {
        "technologies": ["FastAPI", "React", "ESP32", "LSTM"]
    },
    "architecture": {
        "overview": "Multi-tier IoT ingestion architecture."
    },
    "roadmap": {
        "phases": ["Phase 1: Setup", "Phase 2: Dev", "Phase 3: Deploy"]
    }
}

res_pptx = client.post("/api/presentation/generate-pptx", json=pptx_payload)
print(f"\n[1] POST /api/presentation/generate-pptx:")
print(f"    Status: {res_pptx.status_code}")
print(f"    Content-Type: {res_pptx.headers.get('content-type')}")
print(f"    Byte Length: {len(res_pptx.content)} bytes")
assert res_pptx.status_code == 200, f"Expected 200, got {res_pptx.status_code}: {res_pptx.text}"
assert len(res_pptx.content) > 1000, "PPTX file size too small!"
assert "presentationml" in res_pptx.headers.get("content-type", ""), "Wrong content-type for PPTX!"
print("    >>> PPTX GENERATION VERIFIED!")

# 2. Test POST /api/presentation/generate-report (IEEE Markdown)
res_report = client.post("/api/presentation/generate-report", json=pptx_payload)
print(f"\n[2] POST /api/presentation/generate-report:")
print(f"    Status: {res_report.status_code}")
print(f"    Content-Type: {res_report.headers.get('content-type')}")
print(f"    Character Length: {len(res_report.text)} chars")
assert res_report.status_code == 200, f"Expected 200, got {res_report.status_code}: {res_report.text}"
assert len(res_report.text) > 500, "Report markdown too short!"
assert "# Smart Campus Energy Management" in res_report.text or "Smart Campus" in res_report.text
print("    >>> IEEE ACADEMIC REPORT GENERATION VERIFIED!")

# 3. Application restart simulation:
# Create a fresh client and re-query database
from backend.app.db.database import init_db, get_db_connection
init_db()

fresh_client = TestClient(app)
res_restart = fresh_client.get("/api/projects")
assert res_restart.status_code == 200
restarted_count = res_restart.json()["count"]
print(f"\n[3] APPLICATION RESTART SIMULATION:")
print(f"    Re-initialized database connection & fresh TestClient.")
print(f"    Retrieved {restarted_count} projects.")
assert restarted_count == 11, f"Expected 11 projects after restart, got {restarted_count}"
print("    >>> APPLICATION RESTART PERSISTENCE VERIFIED!")

print("\n" + "=" * 60)
print("ALL EXPORT AND RESTART TESTS PASSED!")
print("=" * 60)
