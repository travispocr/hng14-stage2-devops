import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Mock redis before importing main
with patch("redis.Redis") as mock_redis:
    mock_redis.return_value = MagicMock()
    from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis_client():
    with patch("main.r") as mock_r:
        yield mock_r


def test_create_job_returns_job_id(mock_redis_client):
    """POST /jobs should return a job_id"""
    mock_redis_client.lpush.return_value = 1
    mock_redis_client.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format


def test_create_job_sets_queued_status(mock_redis_client):
    """POST /jobs should set job status to queued in Redis"""
    mock_redis_client.lpush.return_value = 1
    mock_redis_client.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    job_id = response.json()["job_id"]
    mock_redis_client.hset.assert_called_once_with(
        f"job:{job_id}", "status", "queued"
    )


def test_get_job_returns_status(mock_redis_client):
    """GET /jobs/:id should return job status"""
    mock_redis_client.hget.return_value = b"completed"

    response = client.get("/jobs/test-job-123")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "completed"


def test_get_job_not_found(mock_redis_client):
    """GET /jobs/:id should return 404 when job does not exist"""
    mock_redis_client.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_create_job_pushes_to_queue(mock_redis_client):
    """POST /jobs should push job_id to Redis queue"""
    mock_redis_client.lpush.return_value = 1
    mock_redis_client.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    job_id = response.json()["job_id"]
    mock_redis_client.lpush.assert_called_once()
    call_args = mock_redis_client.lpush.call_args[0]
    assert job_id in call_args