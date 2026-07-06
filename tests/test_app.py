from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activity_state():
    """Reset the in-memory activities before each test."""
    # Arrange
    original_activities = deepcopy(app_module.activities)
    app_module.activities = deepcopy(original_activities)

    yield

    # Arrange cleanup
    app_module.activities = deepcopy(original_activities)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_root_redirects_to_static_index(client):
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_catalog(client):
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_and_unregister_flow(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_after_signup = client.get("/activities").json()
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )
    activities_after_unregister = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_after_signup[activity_name]["participants"]

    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities_after_unregister[activity_name]["participants"]
