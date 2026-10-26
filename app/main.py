from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="ModelOps Lite")


class JobCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    simulate_failure: bool = False


jobs: dict[str, dict] = {}


# this is an API (get request)

@app.get("/health")
def health_check() -> dict[str,str]:
	"""Return health status of API"""
	return {"status": "okay"}


@app.post("/jobs", status_code=201)
def create_job(request: JobCreate) -> dict:
	job_id = str(uuid4())
	status = "failed" if request.simulate_failure else "completed"
	job = {
		"id": job_id,
		"name": request.name,
		"status": status
	}

	jobs[job_id] = job
	return job

@app.get("/jobs")
def list_jobs() -> list[dict]:
	return list(jobs.values())


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
	job = jobs.get(job_id)

	if job is None:
		raise HTTPException(status_code=404, detail="Job not Found")

	return job
