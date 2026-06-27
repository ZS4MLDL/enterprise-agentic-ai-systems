"""
Module 02 — unit test: settings load correctly and MODE switch works.
"""
import pytest
from app.config.settings import Settings, RuntimeMode


def test_default_mode_is_student():
    s = Settings()
    assert s.MODE == RuntimeMode.STUDENT
    assert not s.is_enterprise


def test_enterprise_mode():
    s = Settings(MODE="enterprise")
    assert s.is_enterprise


def test_db_url_student():
    s = Settings(MODE="student", SQLITE_PATH="./test.db")
    assert "sqlite" in s.db_url


def test_db_url_enterprise():
    s = Settings(MODE="enterprise", DATABASE_URL="postgresql://u:p@localhost/db")
    assert s.db_url == "postgresql://u:p@localhost/db"
