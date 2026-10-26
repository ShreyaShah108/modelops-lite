from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_returns_ok():
	response = client.get("/health")
	
	assert response.status_code == 200
	assert response.json() == {"status": "okay"}


def test_create_job():
	response = client.post("/jobs", json={"name": "test-model-run"})
	assert  response.status_code == 201
	
	data = response.json()
	assert isinstance(data["id"], str)
	assert data["id"] != ""
	assert data["name"] == "test-model-run"
	assert data["status"] == "completed"
	assert "id" in data


def test_create_failed_job():
	response = client.post( "/jobs", json={ "name": "broken-model-run", "simulate_failure": True})
	assert response.status_code == 201
	assert response.json()["status"]=="failed"



def test_get_missing_job_return_404():
	response = client.get("/jobs/not-a-real-job")
	
	assert response.status_code == 404
	assert response.json() == {"detail": "Job not Found"}

def test_create_job_rejects_empty_name():
	response = client.post("/jobs", json={"name": ""})
	
	assert response.status_code == 422

def test_list_jobs_returns_a_list():
    client.post("/jobs", json={"name": "listing-test-job"})

    response = client.get("/jobs")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        job["name"] == "listing-test-job"
        for job in response.json()
    )



def test_create_job_rejects_name_over_100_characters():
	response = client.post(
        "/jobs",
        json={"name": "a" * 101})

	assert response.status_code == 422

def test_create_job_rejects_missing_name():
    response = client.post("/jobs", json={})

    assert response.status_code == 422
