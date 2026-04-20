import pytest
from unittest.mock import MagicMock, patch

# Mock redis before importing app
mock_r = MagicMock()
with patch("redis.Redis", return_value=mock_r):
    from fastapi.testclient import TestClient
    from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mock():
    mock_r.reset_mock()
    yield


def test_create_job_returns_job_id():
    """POST /jobs should return a job_id"""
    mock_r.lpush.return_value = 1
    mock_r.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36


def test_create_job_sets_queued_status():
    """POST /jobs should set job status to queued in Redis"""
    mock_r.lpush.return_value = 1
    mock_r.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    job_id = response.json()["job_id"]
    mock_r.hset.assert_called_once_with(
        f"job:{job_id}", "status", "queued"
    )


def test_get_job_returns_status():
    """GET /jobs/:id should return job status"""
    mock_r.hget.return_value = b"completed"

    response = client.get("/jobs/test-job-123")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "completed"


def test_get_job_not_found():
    """GET /jobs/:id should return 404 when job does not exist"""
    mock_r.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_create_job_pushes_to_queue():
    """POST /jobs should push job_id to Redis queue"""
    mock_r.lpush.return_value = 1
    mock_r.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    job_id = response.json()["job_id"]
    mock_r.lpush.assert_called_once()
    call_args = mock_r.lpush.call_args[0]
    assert job_id in call_args