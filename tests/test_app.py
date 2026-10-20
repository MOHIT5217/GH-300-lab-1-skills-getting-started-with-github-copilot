import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_root_redirects_to_homepage(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details_and_participants(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["existing@mergington.edu"]
    assert response.json()["Art Club"]["participants"] == []


def test_signup_adds_participant(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Art Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in client.get("/activities").json()["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_unregisters_student(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_remove_participant_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_student_not_signed_up(client):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
