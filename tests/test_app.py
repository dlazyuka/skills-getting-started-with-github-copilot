import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 4,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(test_activities))

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 4,
            "participants": ["existing@mergington.edu"],
        }
    }


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@mergington.edu for Chess Club"}
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants == ["existing@mergington.edu", "new@mergington.edu"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 400
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants == ["existing@mergington.edu"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed existing@mergington.edu from Chess Club"}
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants == []


def test_unregister_rejects_unregistered_email(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 404