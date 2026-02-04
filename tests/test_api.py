import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure clean state
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Duplicate sign-up should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Confirm participant present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister participant
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200

    # Unregister again should return 404
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 404


def test_signup_nonexistent_activity():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    resp = client.delete("/activities/Nonexistent/unregister", params={"email": "a@b.com"})
    assert resp.status_code == 404
