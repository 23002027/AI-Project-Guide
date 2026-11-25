"""
Phase 7 — Database Persistence & Authentication Tests.

Verifies:
- PBKDF2 password hashing & verification
- RFC 7519 HMAC-SHA256 JWT encoding & validation
- User registration & duplicate email protection (400)
- User login & invalid credentials protection (401)
- Protected endpoints & Bearer token extraction
- Multi-tenant isolation: User A cannot access or mutate User B's project
- Project CRUD operations and milestone task tracking
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from backend.app.db.database import DatabaseService, init_db


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Unit Tests: Security & Tokens
# ---------------------------------------------------------------------------

def test_password_hashing_and_verification():
    raw_pass = "SecureStudentPass2026!"
    hashed = hash_password(raw_pass)

    assert "$" in hashed
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_creation_and_decoding():
    payload = {"sub": "usr-12345", "email": "test@student.edu", "role": "Lead"}
    token = create_access_token(payload)

    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = decode_access_token(token)
    assert decoded["sub"] == "usr-12345"
    assert decoded["email"] == "test@student.edu"
    assert "exp" in decoded


# ---------------------------------------------------------------------------
# API Integration Tests: Auth Endpoints
# ---------------------------------------------------------------------------

def test_user_registration_and_login_flow(client: TestClient):
    import time
    unique_email = f"student_{int(time.time() * 1000)}@college.edu"

    # 1. Register new user
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "email": unique_email,
            "password": "Password123!",
            "name": "Jane Developer",
            "institution": "National Tech University",
            "role": "AI Lead",
        },
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == unique_email
    assert "hashed_password" not in reg_data["user"]
    token = reg_data["access_token"]

    # 2. Duplicate registration should be rejected with 400
    dup_resp = client.post(
        "/api/auth/register",
        json={
            "email": unique_email,
            "password": "AnotherPassword!",
            "name": "Duplicate User",
        },
    )
    assert dup_resp.status_code == 400

    # 3. Login with correct credentials
    login_resp = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 4. Login with incorrect password should be rejected with 401
    bad_login = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    # 5. Access protected /me endpoint with valid token
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == unique_email

    # 6. Access protected endpoint without token should return 401
    unauth_resp = client.get("/api/auth/me")
    assert unauth_resp.status_code == 401


# ---------------------------------------------------------------------------
# API Integration Tests: Projects & Multi-Tenant Isolation
# ---------------------------------------------------------------------------

def test_multi_tenant_project_and_task_crud(client: TestClient):
    import time
    email_a = f"usera_{int(time.time() * 1000)}@test.edu"
    email_b = f"userb_{int(time.time() * 1000)}@test.edu"

    # Register User A
    token_a = client.post(
        "/api/auth/register",
        json={"email": email_a, "password": "passA123!", "name": "User A"},
    ).json()["access_token"]

    # Register User B
    token_b = client.post(
        "/api/auth/register",
        json={"email": email_b, "password": "passB123!", "name": "User B"},
    ).json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User A creates a project
    create_resp = client.post(
        "/api/projects",
        headers=headers_a,
        json={
            "title": "Smart Traffic Signal AI",
            "domain": "AI / Machine Learning",
            "description": "Reinforcement learning traffic control system",
            "deadline": "2 months",
            "team_size": 2,
        },
    )
    assert create_resp.status_code == 201
    proj_a = create_resp.json()
    proj_a_id = proj_a["id"]
    assert proj_a["title"] == "Smart Traffic Signal AI"

    # 2. User A can retrieve project
    get_resp = client.get(f"/api/projects/{proj_a_id}", headers=headers_a)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == proj_a_id

    # 3. User B CANNOT retrieve User A's project (Isolation Enforcement)
    sec_resp = client.get(f"/api/projects/{proj_a_id}", headers=headers_b)
    assert sec_resp.status_code == 404

    # 4. User A updates progress
    update_resp = client.put(
        f"/api/projects/{proj_a_id}",
        headers=headers_a,
        json={"progress": 60},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["progress"] == 60

    # 5. User A adds a milestone task
    task_resp = client.post(
        f"/api/projects/{proj_a_id}/tasks",
        headers=headers_a,
        json={"title": "Train DQN model in Simulation", "category": "ai"},
    )
    assert task_resp.status_code == 201
    task_id = task_resp.json()["id"]
    assert task_resp.json()["status"] == "pending"

    # 6. User A marks task completed
    task_update = client.put(
        f"/api/projects/{proj_a_id}/tasks/{task_id}",
        headers=headers_a,
        json={"status": "completed"},
    )
    assert task_update.status_code == 200
    assert task_update.json()["status"] == "completed"

    # 7. User A lists tasks
    tasks_list = client.get(f"/api/projects/{proj_a_id}/tasks", headers=headers_a)
    assert tasks_list.status_code == 200
    assert tasks_list.json()["count"] >= 1

    # 8. User B CANNOT delete User A's project
    del_forbidden = client.delete(f"/api/projects/{proj_a_id}", headers=headers_b)
    assert del_forbidden.status_code == 404

    # 9. User A deletes project
    del_resp = client.delete(f"/api/projects/{proj_a_id}", headers=headers_a)
    assert del_resp.status_code == 200
