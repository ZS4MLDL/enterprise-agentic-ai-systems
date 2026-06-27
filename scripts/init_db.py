"""
Bootstrap script — creates the data/ directory and (for student mode) the SQLite DB.
Run once after cloning: python scripts/init_db.py
"""
import os
from pathlib import Path

from app.config.settings import get_settings

s = get_settings()

Path("data/documents").mkdir(parents=True, exist_ok=True)
Path("data/chroma").mkdir(parents=True, exist_ok=True)

if not s.is_enterprise:
    db_path = Path(s.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Student mode: SQLite will be created at {db_path} on first run.")
else:
    print(f"Enterprise mode: ensure Postgres is running at {s.DATABASE_URL}")
    print("Run: alembic upgrade head")

print("Init complete.")
