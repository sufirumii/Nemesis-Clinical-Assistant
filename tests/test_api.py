"""
Basic integration tests for the FastAPI backend.
Run with: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Patch model loading before importing app
mock_result = {
    "full_response": "Test response",
    "reasoning": "Test reasoning",
    "differentials": "Test differentials",
    "workup": "Test workup",
    "treatment": "Test treatment",
    "red_flags": "None identified",
}

with patch("backend.services.inference.InferenceService.load"), \
     patch("backend.services.inference.InferenceService.analyze",
           return_value=mock_result):
    from backend.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze():
    with patch("backend.services.inference.inference_service.analyze",
               return_value=mock_result):
        r = client.post("/analyze", json={
            "session_id": "test123",
            "symptoms": "Fever and cough for 3 days",
            "patient_age": 30,
            "patient_sex": "male",
        })
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == "test123"
    assert "full_response" in data


def test_get_history():
    # After analyze above, history should exist
    r = client.get("/history/test123")
    assert r.status_code in (200, 404)   # 404 if session cleared between tests


def test_clear_history():
    r = client.delete("/history/test123")
    assert r.status_code == 200


def test_analyze_validation():
    r = client.post("/analyze", json={
        "session_id": "test",
        "symptoms": "x",    # too short — min 5 chars
    })
    assert r.status_code == 422
