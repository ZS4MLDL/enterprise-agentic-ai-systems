"""
Agent runtime — session lifecycle management (Module 04).
Wraps the research agent with session tracking in the database.
"""
import uuid
from app.db.session import get_session
from app.db.models import ConversationSession
from app.config.settings import get_settings


def create_session() -> str:
    """Create a new session ID and persist it to the DB."""
    session_id = str(uuid.uuid4())
    with get_session() as db:
        db.add(ConversationSession(
            id=session_id,
            mode=get_settings().MODE.value,
        ))
        db.commit()
    return session_id


def get_or_create_session(session_id: str) -> str:
    """Return existing session or create it if it doesn't exist yet."""
    with get_session() as db:
        existing = db.get(ConversationSession, session_id)
        if not existing:
            db.add(ConversationSession(
                id=session_id,
                mode=get_settings().MODE.value,
            ))
            db.commit()
    return session_id


def increment_turn(session_id: str) -> None:
    """Increment turn counter for a session."""
    with get_session() as db:
        session = db.get(ConversationSession, session_id)
        if session:
            session.turn_count += 1
            db.commit()
