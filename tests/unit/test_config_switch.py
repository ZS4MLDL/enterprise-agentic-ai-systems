"""
Module 04 — config switch tests.
Verifies that student and enterprise modes load the correct backends.
"""
from app.config.settings import Settings, RuntimeMode


def test_student_mode_uses_sqlite():
    s = Settings(MODE="student", SQLITE_PATH="./data/test.db")
    assert "sqlite" in s.db_url
    assert not s.is_enterprise


def test_enterprise_mode_uses_postgres():
    s = Settings(MODE="enterprise", DATABASE_URL="postgresql://u:p@localhost/db")
    assert "postgresql" in s.db_url
    assert s.is_enterprise


def test_mode_switch_does_not_require_code_change():
    """The only thing that should change between modes is the env var."""
    student = Settings(MODE="student")
    enterprise = Settings(MODE="enterprise", DATABASE_URL="postgresql://u:p@localhost/db")
    assert student.db_url != enterprise.db_url


def test_student_mode_is_default():
    s = Settings()
    assert s.MODE == RuntimeMode.STUDENT
