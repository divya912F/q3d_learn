"""Smoke tests for the v2.4 finale features: chat, leaderboard, authoring, tests,
projects, LeetCode practice and institution (SSO) mode."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["AI_PROVIDER"] = "offline"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def instructor(client):
    return client.post("/api/users", json={"name": "Prof X", "role": "instructor"}).json()


@pytest.fixture(scope="module")
def classroom(client, instructor):
    return client.post("/api/classrooms", json={"name": "Finale Class", "instructor_id": instructor["id"]}).json()


def test_leaderboard_all(client):
    r = client.get("/api/leaderboard/all")
    assert r.status_code == 200
    assert "entries" in r.json()


def test_community_chat(client, classroom):
    code = classroom["code"]
    assert client.get(f"/api/classrooms/{code}/chat").json()["messages"] == []
    sent = client.post(f"/api/classrooms/{code}/chat", json={"name": "Ada", "body": "hello world"})
    assert sent.status_code == 200
    msgs = client.get(f"/api/classrooms/{code}/chat").json()["messages"]
    assert msgs and msgs[0]["body"] == "hello world"


def test_authoring(client, instructor):
    c = client.post("/api/authoring/courses", json={"title": "My Course", "summary": "s", "instructor_id": instructor["id"]})
    assert c.status_code == 200
    cid = c.json()["id"]
    l = client.post(f"/api/authoring/courses/{cid}/lessons",
                    json={"title": "Lesson 1", "video_url": "https://youtu.be/dQw4w9WgXcQ", "instructor_id": instructor["id"]})
    assert l.status_code == 200
    detail = client.get(f"/api/authoring/courses/{cid}").json()
    assert len(detail["lessons"]) == 1
    assert detail["lessons"][0]["video_url"].endswith("dQw4w9WgXcQ")


def test_tests_flow(client, instructor):
    body = {"title": "Quiz", "instructor_id": instructor["id"], "questions": [
        {"prompt": "2+2?", "options": ["3", "4", "5"], "answer": 1, "explain": "basic"}]}
    t = client.post("/api/tests", json=body)
    assert t.status_code == 200
    tid = t.json()["id"]
    taking = client.get(f"/api/tests/{tid}").json()
    assert "answer" not in taking["questions"][0]  # answers hidden when taking
    res = client.post(f"/api/tests/{tid}/submit", json={"name": "Bob", "answers": [1]})
    assert res.json()["score"] == 1 and res.json()["percent"] == 100
    assert client.get(f"/api/tests/{tid}/results").json()[0]["name"] == "Bob"


def test_projects(client):
    data = client.get("/api/projects/quantum").json()
    assert data["projects"] and "id" in data["projects"][0]


def test_leetcode(client):
    data = client.get("/api/leetcode/dsa").json()
    assert len(data["problems"]) > 5
    assert data["problems"][0]["url"].startswith("https://leetcode.com/")


def test_institution_sso(client):
    inst = client.post("/api/institutions", json={"name": "MIET", "admin_name": "Dean"}).json()
    code = inst["code"]
    login = client.post("/api/institutions/sso", json={"code": code, "name": "Sam", "email": "sam@x.edu", "role": "student"})
    assert login.status_code == 200
    assert login.json()["user"]["name"] == "Sam"
    overview = client.get(f"/api/institutions/{code}").json()
    assert overview["count"] == 1 and overview["members"][0]["email"] == "sam@x.edu"


def test_institution_domain_guard(client):
    inst = client.post("/api/institutions", json={"name": "Domain U", "domain": "domain.edu"}).json()
    bad = client.post("/api/institutions/sso", json={"code": inst["code"], "name": "Z", "email": "z@other.com"})
    assert bad.status_code == 403
