import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before/after each test."""
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic expected key from sample data
    assert "Chess Club" in data


def test_signup_and_prevent_duplicate():
    email = "testuser@example.com"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    # second signup should return 400 (duplicate)
    resp2 = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister():
    # unregister an existing participant
    email = activities["Chess Club"]["participants"][0]
    resp = client.post("/activities/Chess Club/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

    # attempt to unregister someone not in the list
    resp2 = client.post("/activities/Chess Club/unregister", params={"email": "noone@example.com"})
    assert resp2.status_code == 404
