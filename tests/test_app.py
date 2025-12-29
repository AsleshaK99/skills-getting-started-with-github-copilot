from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function():
    # Reset participants to a known state before each test
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Soccer Team"]["participants"] = []


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate_signup():
    # signup a new student to Soccer Team
    r = client.post("/activities/Soccer Team/signup?email=test@student.edu")
    assert r.status_code == 200
    assert "Signed up test@student.edu for Soccer Team" in r.json()["message"]

    # duplicate signup should fail with 400
    r2 = client.post("/activities/Soccer Team/signup?email=test@student.edu")
    assert r2.status_code == 400
    assert "already signed up" in r2.json()["detail"]


def test_unregister_student():
    # unregister an existing student from Chess Club
    r = client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
    assert r.status_code == 200
    assert "Unregistered michael@mergington.edu from Chess Club" in r.json()["message"]

    # attempt to unregister someone not signed up
    r2 = client.post("/activities/Chess Club/unregister?email=not@there.edu")
    assert r2.status_code == 400
    assert "not signed up" in r2.json()["detail"]


def test_activity_not_found():
    r = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert r.status_code == 404

    r2 = client.post("/activities/NoSuchActivity/unregister?email=a@b.com")
    assert r2.status_code == 404
