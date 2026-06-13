"""
Backend unit tests for FinSense AI.
Run: cd backend && pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, verify_password, create_access_token

client = TestClient(app)


# ── Security Tests ────────────────────────────────────────────────────

def test_password_hashing():
    plain = "MySecret123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_token_creation():
    token = create_access_token({"sub": "42"})
    assert isinstance(token, str)
    assert len(token) > 20


# ── Auth Endpoint Tests ───────────────────────────────────────────────

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_register_and_login():
    import uuid
    uid = uuid.uuid4().hex[:8]
    # Register
    res = client.post("/api/v1/auth/register", json={
        "email": f"{uid}@test.com",
        "username": uid,
        "password": "TestPass123!",
    })
    assert res.status_code == 201
    assert res.json()["email"] == f"{uid}@test.com"

    # Login
    res = client.post("/api/v1/auth/login", json={
        "email": f"{uid}@test.com",
        "password": "TestPass123!",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_duplicate_email_rejected():
    res = client.post("/api/v1/auth/register", json={
        "email": "duplicate@test.com",
        "username": "dup1",
        "password": "TestPass123!",
    })
    # Second registration with same email
    res2 = client.post("/api/v1/auth/register", json={
        "email": "duplicate@test.com",
        "username": "dup2",
        "password": "TestPass123!",
    })
    # First may succeed or fail depending on DB state; second should fail if first succeeded
    if res.status_code == 201:
        assert res2.status_code == 400


def test_protected_endpoint_without_token():
    res = client.get("/api/v1/expenses")
    assert res.status_code == 401


# ── NLP Categorizer Tests ─────────────────────────────────────────────

def test_nlp_categorizer_food():
    from app.services.nlp_categorizer import categorize_expense
    category, confidence = categorize_expense("Swiggy order biryani")
    assert category == "Food"
    assert 0 < confidence <= 1.0


def test_nlp_categorizer_transport():
    from app.services.nlp_categorizer import categorize_expense
    category, _ = categorize_expense("Uber cab ride")
    assert category == "Transport"


def test_nlp_empty_input():
    from app.services.nlp_categorizer import categorize_expense
    category, confidence = categorize_expense("")
    assert category == "Miscellaneous"
    assert confidence == 0.5


# ── Financial Health Score Tests ──────────────────────────────────────

def test_health_score_range():
    from app.services.health_score import compute_financial_health
    score, breakdown, explanation = compute_financial_health([], [])
    assert 0 <= score <= 100
    assert isinstance(breakdown, dict)
    assert isinstance(explanation, str)
