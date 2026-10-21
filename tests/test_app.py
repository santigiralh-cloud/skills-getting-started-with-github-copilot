import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ACTIVITY_NAME = "Test Activity"
EXISTING_EMAIL = "existing@example.com"
NEW_EMAIL = "new@example.com"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "An activity for API tests",
            "schedule": "Mondays at 3:00 PM",
            "max_participants": 10,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    # Arreglar
    expected_activity = {
        "description": "An activity for API tests",
        "schedule": "Mondays at 3:00 PM",
        "max_participants": 10,
        "participants": [EXISTING_EMAIL],
    }

    # Actuar
    response = client.get("/activities")

    # Afirmar
    assert response.status_code == 200
    assert response.json() == {ACTIVITY_NAME: expected_activity}


def test_signup_adds_participant(client):
    # Arreglar
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"

    # Actuar
    response = client.post(signup_url, params={"email": NEW_EMAIL})

    # Afirmar
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {NEW_EMAIL} for {ACTIVITY_NAME}"
    }
    assert NEW_EMAIL in client.get("/activities").json()[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arreglar
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"

    # Actuar
    response = client.post(signup_url, params={"email": EXISTING_EMAIL})

    # Afirmar
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arreglar
    unknown_activity = "Unknown Activity"

    # Actuar
    response = client.post(
        f"/activities/{unknown_activity}/signup", params={"email": NEW_EMAIL}
    )

    # Afirmar
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_cancel_signup_removes_participant(client):
    # Arreglar
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"

    # Actuar
    response = client.delete(signup_url, params={"email": EXISTING_EMAIL})

    # Afirmar
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Canceled {EXISTING_EMAIL}'s signup for {ACTIVITY_NAME}"
    }
    assert EXISTING_EMAIL not in client.get("/activities").json()[ACTIVITY_NAME]["participants"]


def test_cancel_signup_rejects_unregistered_participant(client):
    # Arreglar
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"

    # Actuar
    response = client.delete(signup_url, params={"email": NEW_EMAIL})

    # Afirmar
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_cancel_signup_rejects_unknown_activity(client):
    # Arreglar
    unknown_activity = "Unknown Activity"

    # Actuar
    response = client.delete(
        f"/activities/{unknown_activity}/signup", params={"email": EXISTING_EMAIL}
    )

    # Afirmar
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"