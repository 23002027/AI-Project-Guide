"""
Database Persistence Module (Phase 7).

Provides SQLite relational persistence for multi-tenant users, projects,
hackathons, tasks, artifacts, and multi-agent workflow records.
Executes thread-safe asynchronous database operations via asyncio.to_thread.
"""

import os
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Ensure database directory and path resolution
ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_FILE = BACKEND_DIR / "data" / "copilot.db"

env_db_path = os.getenv("DATABASE_PATH")
if env_db_path:
    p = Path(env_db_path)
    if p.is_absolute():
        DATABASE_URL = str(p.resolve())
    else:
        if (ROOT_DIR / env_db_path).parent.exists() or (ROOT_DIR / env_db_path).exists():
            DATABASE_URL = str((ROOT_DIR / env_db_path).resolve())
        elif (BACKEND_DIR / env_db_path).parent.exists() or (BACKEND_DIR / env_db_path).exists():
            DATABASE_URL = str((BACKEND_DIR / env_db_path).resolve())
        else:
            DATABASE_URL = str((ROOT_DIR / env_db_path).resolve())
else:
    DATABASE_URL = str(DEFAULT_DB_FILE.resolve())

Path(DATABASE_URL).parent.mkdir(parents=True, exist_ok=True)


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create a new SQLite connection with row factory and foreign keys enabled."""
    path = db_path or DATABASE_URL
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database schema tables and indexes."""
    path = db_path or DATABASE_URL
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        name TEXT NOT NULL,
        institution TEXT DEFAULT 'Engineering Institute',
        role TEXT DEFAULT 'Student Developer',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        domain TEXT NOT NULL,
        description TEXT,
        experience_level TEXT DEFAULT 'Intermediate',
        deadline TEXT DEFAULT '3 months',
        budget TEXT DEFAULT 'Free Tier',
        is_team INTEGER DEFAULT 0,
        team_size INTEGER DEFAULT 1,
        progress INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS hackathons (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        hackathon_name TEXT NOT NULL,
        problem_statement TEXT NOT NULL,
        domain TEXT DEFAULT 'AI/ML',
        duration TEXT DEFAULT '24 hours',
        team_size INTEGER DEFAULT 3,
        team_skills TEXT DEFAULT 'Python, React',
        budget TEXT DEFAULT 'Free Tier',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS project_artifacts (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        artifact_type TEXT NOT NULL,
        content_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS hackathon_artifacts (
        id TEXT PRIMARY KEY,
        hackathon_id TEXT NOT NULL,
        artifact_type TEXT NOT NULL,
        content_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (hackathon_id) REFERENCES hackathons(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        category TEXT DEFAULT 'backend',
        status TEXT DEFAULT 'pending',
        assigned_to TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS workflow_records (
        id TEXT PRIMARY KEY,
        session_id TEXT UNIQUE NOT NULL,
        user_id TEXT,
        workflow_type TEXT NOT NULL,
        status TEXT NOT NULL,
        current_agent TEXT,
        results_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
    CREATE INDEX IF NOT EXISTS idx_hackathons_user ON hackathons(user_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
    CREATE INDEX IF NOT EXISTS idx_artifacts_project ON project_artifacts(project_id);
    """)

    conn.commit()
    conn.close()


# Initialize tables on import
init_db()


# ---------------------------------------------------------------------------
# Asynchronous Database CRUD Operations
# ---------------------------------------------------------------------------

class DatabaseService:
    """Async wrapper around SQLite queries."""

    # --- Users ---
    @staticmethod
    async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        def _insert():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()
                user_id = user_data.get("id") or f"usr-{os.urandom(6).hex()}"
                cursor.execute(
                    """
                    INSERT INTO users (id, email, hashed_password, name, institution, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        user_data["email"].lower().strip(),
                        user_data["hashed_password"],
                        user_data["name"],
                        user_data.get("institution", "Engineering Institute"),
                        user_data.get("role", "Student Developer"),
                        now,
                    )
                )
                conn.commit()
                return DatabaseService._get_user_by_id_sync(conn, user_id)
        return await asyncio.to_thread(_insert)

    @staticmethod
    def _get_user_by_id_sync(conn: sqlite3.Connection, user_id: str) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, institution, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        def _get():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
                row = cursor.fetchone()
                return dict(row) if row else None
        return await asyncio.to_thread(_get)

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            with get_db_connection() as conn:
                return DatabaseService._get_user_by_id_sync(conn, user_id)
        return await asyncio.to_thread(_get)

    # --- Projects ---
    @staticmethod
    def get_default_user_id() -> str:
        """
        Dynamically discovers the active workspace user ID:
        1. Checks existing projects in the local database for their user_id.
        2. Falls back to the earliest user in the users table.
        3. If no user exists, creates a local workspace user to satisfy foreign keys.
        Never hardcodes an assumed user ID.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM projects ORDER BY created_at ASC LIMIT 1;")
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]

            cursor.execute("SELECT id FROM users ORDER BY created_at ASC LIMIT 1;")
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]

            local_id = f"usr-{os.urandom(6).hex()}"
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                """
                INSERT INTO users (id, email, hashed_password, name, institution, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (local_id, "local@projectguide.local", "", "Local Engineer", "Engineering Workspace", "Local User", now)
            )
            conn.commit()
            return local_id

    @staticmethod
    async def create_project(user_id: str, proj: Dict[str, Any]) -> Dict[str, Any]:
        def _create():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                proj_id = proj.get("id") or f"proj-{os.urandom(6).hex()}"
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    """
                    INSERT INTO projects (
                        id, user_id, title, domain, description, experience_level,
                        deadline, budget, is_team, team_size, progress, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        proj_id,
                        user_id,
                        proj["title"],
                        proj.get("domain", "AI / Machine Learning"),
                        proj.get("description", ""),
                        proj.get("experience_level", "Intermediate"),
                        proj.get("deadline", "3 months"),
                        proj.get("budget", "Free Tier"),
                        1 if proj.get("is_team") else 0,
                        proj.get("team_size", 1),
                        proj.get("progress", 0),
                        now,
                        now,
                    )
                )
                conn.commit()
                return DatabaseService._get_project_sync(conn, proj_id)
        return await asyncio.to_thread(_create)

    @staticmethod
    def _get_project_sync(conn: sqlite3.Connection, project_id: str) -> Optional[Dict[str, Any]]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    async def get_project(project_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            with get_db_connection() as conn:
                return DatabaseService._get_project_sync(conn, project_id)
        return await asyncio.to_thread(_get)

    @staticmethod
    async def list_user_projects(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists projects.
        In local single-user mode (user_id is None): returns all projects in the workspace.
        If user_id is provided: filters by that user_id.
        """
        def _list():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute("SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
                else:
                    cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
                return [dict(r) for r in cursor.fetchall()]
        return await asyncio.to_thread(_list)

    list_projects = list_user_projects

    @staticmethod
    async def update_project(project_id: str, updates: Dict[str, Any], user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                # Check ownership only when a specific user_id is enforced
                if user_id and row["user_id"] != user_id:
                    return None

                fields = []
                values = []
                for k, v in updates.items():
                    if k in ("title", "domain", "description", "progress", "deadline", "budget", "team_size"):
                        fields.append(f"{k} = ?")
                        values.append(v)

                if fields:
                    fields.append("updated_at = ?")
                    values.append(datetime.now(timezone.utc).isoformat())
                    values.append(project_id)
                    cursor.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", tuple(values))
                    conn.commit()

                return DatabaseService._get_project_sync(conn, project_id)
        return await asyncio.to_thread(_update)

    @staticmethod
    async def delete_project(project_id: str, user_id: Optional[str] = None) -> bool:
        def _delete():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                if user_id and row["user_id"] != user_id:
                    return False
                cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
                conn.commit()
                return True
        return await asyncio.to_thread(_delete)

    # --- Tasks ---
    @staticmethod
    async def add_task(project_id: str, title: str, category: str = "backend") -> Dict[str, Any]:
        def _add():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                task_id = f"tsk-{os.urandom(6).hex()}"
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    """
                    INSERT INTO tasks (id, project_id, title, category, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'pending', ?, ?)
                    """,
                    (task_id, project_id, title, category, now, now)
                )
                conn.commit()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                return dict(cursor.fetchone())
        return await asyncio.to_thread(_add)

    @staticmethod
    async def list_project_tasks(project_id: str) -> List[Dict[str, Any]]:
        def _list():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at ASC", (project_id,))
                return [dict(r) for r in cursor.fetchall()]
        return await asyncio.to_thread(_list)

    @staticmethod
    async def update_task_status(task_id: str, status: str) -> Optional[Dict[str, Any]]:
        def _update():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (status, now, task_id))
                conn.commit()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        return await asyncio.to_thread(_update)

    @staticmethod
    async def delete_task(task_id: str) -> bool:
        def _del():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        return await asyncio.to_thread(_del)

    # --- Artifacts & Notes ---
    @staticmethod
    async def save_artifact(project_id: str, artifact_type: str, content_json: str) -> Dict[str, Any]:
        def _save():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                art_id = f"art-{os.urandom(6).hex()}"
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    """
                    INSERT INTO project_artifacts (id, project_id, artifact_type, content_json, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (art_id, project_id, artifact_type, content_json, now)
                )
                conn.commit()
                cursor.execute("SELECT * FROM project_artifacts WHERE id = ?", (art_id,))
                return dict(cursor.fetchone())
        return await asyncio.to_thread(_save)

    @staticmethod
    async def list_project_artifacts(project_id: str) -> List[Dict[str, Any]]:
        def _list():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM project_artifacts WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
                return [dict(r) for r in cursor.fetchall()]
        return await asyncio.to_thread(_list)
