"""
Returns the correct LangGraph checkpointer based on MODE (Module 03).

Student    → SqliteSaver     requires: langgraph-checkpoint-sqlite
Enterprise → PostgresSaver   requires: langgraph-checkpoint-postgres
                             install:  pip install -r requirements-enterprise-db.txt
"""
from pathlib import Path
from app.config.settings import get_settings


def get_checkpointer():
    s = get_settings()

    if s.is_enterprise:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
        except ImportError:
            raise ImportError(
                "Enterprise mode requires langgraph-checkpoint-postgres. "
                "Run: pip install -r requirements-enterprise-db.txt"
            )
        return PostgresSaver.from_conn_string(s.DATABASE_URL)

    # Student mode — SQLite
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        raise ImportError(
            "langgraph-checkpoint-sqlite is missing. "
            "Run: pip install -r requirements.txt"
        )
    db_path = Path(s.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver.from_conn_string(str(db_path))
