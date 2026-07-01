"""
Module 04 — migration tests.
Tests that Alembic can migrate up, down, and back up against SQLite.
"""
import os
import sqlite3
import tempfile
from pathlib import Path


def run_alembic(command: list[str], db_path: str) -> int:
    """Run an alembic command with a temp SQLite DB."""
    import subprocess, sys
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
    env["SQLITE_PATH"] = db_path
    env["MODE"] = "student"
    result = subprocess.run(
        [sys.executable, "-m", "alembic"] + command,
        cwd=str(Path(__file__).resolve().parents[2]),
        env=env,
        capture_output=True,
    )
    return result.returncode


def test_migrate_up_creates_tables():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        assert run_alembic(["upgrade", "head"], db_path) == 0
        conn = sqlite3.connect(db_path)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "conversation_sessions" in tables
        assert "audit_log" in tables
    finally:
        os.unlink(db_path)


def test_migrate_down_removes_tables():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        run_alembic(["upgrade", "head"], db_path)
        assert run_alembic(["downgrade", "-1"], db_path) == 0
        conn = sqlite3.connect(db_path)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "conversation_sessions" not in tables
        assert "audit_log" not in tables
    finally:
        os.unlink(db_path)


def test_migrate_up_after_rollback():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        run_alembic(["upgrade", "head"], db_path)
        run_alembic(["downgrade", "-1"], db_path)
        assert run_alembic(["upgrade", "head"], db_path) == 0
        conn = sqlite3.connect(db_path)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        assert "conversation_sessions" in tables
    finally:
        os.unlink(db_path)
