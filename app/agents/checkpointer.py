"""
Returns the correct LangGraph checkpointer based on MODE (Module 03).

Student  → SqliteSaver  (file-backed, zero infrastructure)
Enterprise → PostgresSaver (Postgres-backed, survives process restarts)
"""
from pathlib import Path
from app.config.settings import get_settings


def get_checkpointer():
    s = get_settings()

    if s.is_enterprise:
        from langgraph.checkpoint.postgres import PostgresSaver
        return PostgresSaver.from_conn_string(s.DATABASE_URL)

    # Student mode — SQLite
    from langgraph.checkpoint.sqlite import SqliteSaver
    db_path = Path(s.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver.from_conn_string(str(db_path))
