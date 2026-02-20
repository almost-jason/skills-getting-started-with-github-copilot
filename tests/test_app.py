import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_map(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Basketball Team" in payload


def test_signup_adds_participant(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Basketball%20Team/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Basketball Team"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    existing_email = activities["Basketball Team"]["participants"][0]

    response = client.post("/activities/Basketball%20Team/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_removes_participant(client):
    email = activities["Soccer Club"]["participants"][0]

    response = client.delete("/activities/Soccer%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Soccer Club"]["participants"]


def test_unregister_requires_existing_participant(client):
    response = client.delete(
        "/activities/Soccer%20Club/signup", params={"email": "absent@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
