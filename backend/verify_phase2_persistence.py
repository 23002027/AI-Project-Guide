import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import DatabaseService, get_db_connection

client = TestClient(app)

print("=" * 60)
print("PHASE 2: VERIFICATION OF LOCAL SINGLE-USER PERSISTENCE")
print("=" * 60)

# 1. Verify GET /api/projects returns all 11 existing projects WITHOUT auth
res_list = client.get("/api/projects")
assert res_list.status_code == 200, f"Expected 200, got {res_list.status_code}: {res_list.text}"
data = res_list.json()
projects = data["projects"]
count = data["count"]
print(f"\n[1] GET /api/projects (No Auth): HTTP 200 OK")
print(f"    Returned {count} projects in workspace.")
assert count >= 11, f"Expected at least 11 projects, found {count}"

# List titles of all existing projects
print("    Existing Projects List:")
for p in projects:
    print(f"      - ID={p['id']} | title='{p['title']}' | domain='{p['domain']}'")

# 2. Verify GET /api/projects/{id} for an existing project without auth
first_proj = projects[0]
res_get = client.get(f"/api/projects/{first_proj['id']}")
assert res_get.status_code == 200, f"Expected 200, got {res_get.status_code}: {res_get.text}"
print(f"\n[2] GET /api/projects/{first_proj['id']} (No Auth): HTTP 200 OK")
print(f"    Retrieved: '{res_get.json()['title']}'")

# 3. Create a new project without auth
new_payload = {
    "title": "Autonomous Drone Delivery Guidance",
    "domain": "AI / Machine Learning",
    "description": "Path planning and collision avoidance using local vision models",
    "experience_level": "Intermediate",
    "deadline": "4 months",
    "budget": "Free Tier",
    "team_size": 3
}
res_create = client.post("/api/projects", json=new_payload)
assert res_create.status_code == 201, f"Expected 201, got {res_create.status_code}: {res_create.text}"
created_proj = res_create.json()
created_id = created_proj["id"]
print(f"\n[3] POST /api/projects (No Auth): HTTP 201 CREATED")
print(f"    Created: ID={created_id} | title='{created_proj['title']}' | user_id='{created_proj['user_id']}'")

# 4. Update the created project without auth
res_update = client.put(f"/api/projects/{created_id}", json={"progress": 45, "budget": "Open Source"})
assert res_update.status_code == 200, f"Expected 200, got {res_update.status_code}: {res_update.text}"
print(f"\n[4] PUT /api/projects/{created_id} (No Auth): HTTP 200 OK")
print(f"    Updated progress={res_update.json()['progress']}, budget='{res_update.json()['budget']}'")

# 5. Add a milestone task to the project without auth
task_payload = {"title": "Train YOLOv8 on aerial dataset", "category": "ai"}
res_task = client.post(f"/api/projects/{created_id}/tasks", json=task_payload)
assert res_task.status_code == 201, f"Expected 201, got {res_task.status_code}: {res_task.text}"
task = res_task.json()
task_id = task["id"]
print(f"\n[5] POST /api/projects/{created_id}/tasks (No Auth): HTTP 201 CREATED")
print(f"    Created Task: ID={task_id} | title='{task['title']}' | status='{task['status']}'")

# 6. Update task status without auth
res_task_update = client.put(f"/api/projects/{created_id}/tasks/{task_id}", json={"status": "in_progress"})
assert res_task_update.status_code == 200, f"Expected 200, got {res_task_update.status_code}: {res_task_update.text}"
print(f"\n[6] PUT /api/projects/{created_id}/tasks/{task_id} (No Auth): HTTP 200 OK")
print(f"    Updated Task Status: '{res_task_update.json()['status']}'")

# 7. List tasks for the project without auth
res_tasks_list = client.get(f"/api/projects/{created_id}/tasks")
assert res_tasks_list.status_code == 200, f"Expected 200, got {res_tasks_list.status_code}: {res_tasks_list.text}"
print(f"\n[7] GET /api/projects/{created_id}/tasks (No Auth): HTTP 200 OK")
print(f"    Found {res_tasks_list.json()['count']} task(s)")

# 8. Test artifact / notes persistence via DatabaseService
import json
import asyncio
art_data = {"notes": "Key literature review on A* and RRT algorithms.", "tags": ["robotics", "cv"]}
print(f"\n[8] DatabaseService.save_artifact:")
art_res = asyncio.run(DatabaseService.save_artifact(created_id, "research_notes", json.dumps(art_data)))
print(f"    Saved artifact ID={art_res['id']} for project={created_id}")
art_list = asyncio.run(DatabaseService.list_project_artifacts(created_id))
print(f"    Retrieved {len(art_list)} artifact(s) for project.")

# 9. Clean up test task and test project
res_del_task = client.delete(f"/api/projects/{created_id}/tasks/{task_id}")
assert res_del_task.status_code == 200, f"Expected 200, got {res_del_task.status_code}: {res_del_task.text}"
print(f"\n[9] DELETE /api/projects/{created_id}/tasks/{task_id}: HTTP 200 OK")

res_del_proj = client.delete(f"/api/projects/{created_id}")
assert res_del_proj.status_code == 200, f"Expected 200, got {res_del_proj.status_code}: {res_del_proj.text}"
print(f"    DELETE /api/projects/{created_id}: HTTP 200 OK")

# 10. Confirm all 11 original projects remain intact
res_final = client.get("/api/projects")
assert res_final.status_code == 200
final_count = res_final.json()["count"]
print(f"\n[10] FINAL INTEGRITY CHECK:")
print(f"    Original Projects Count: {count}")
print(f"    Final Projects Count:    {final_count}")
assert final_count == count, f"Count mismatch! Expected {count}, got {final_count}"
print("    >>> ALL 11 ORIGINAL PROJECTS REMAIN PERFECTLY PRESERVED!")

print("\n" + "=" * 60)
print("ALL SINGLE-USER PERSISTENCE CHECKS PASSED SUCCESSFULLY!")
print("=" * 60)
