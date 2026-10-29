# ModelOps Lite

**A containerised data-quality analysis API built with FastAPI, Docker, and Kubernetes.**

ModelOps Lite is a lightweight service that analyses CSV datasets and generates data-quality reports. It helps users quickly identify missing values, duplicate rows, and basic column data types before using a dataset for analytics or machine learning.

The project also explores practical software engineering and operations concepts, including automated testing, containerisation, Kubernetes deployments, health checks, and continuous integration.

## Features

### CSV data-quality analysis

Upload a CSV file through `POST /analyze-csv` to receive a JSON report containing:

- Total number of rows and columns
- Column names
- Missing-value counts for each column
- Number of duplicate rows
- Basic column-type inference (`numeric` or `text`)

The endpoint validates file extensions, UTF-8 encoding, column headers, duplicate column names, and a maximum upload size of 5 MB.

### Job management API

The original API also supports basic job operations:

- Create a job with `POST /jobs`
- List jobs with `GET /jobs`
- Retrieve a job with `GET /jobs/{job_id}`
- Simulate a failed job for testing

Job statuses are currently held in memory and are not connected to the CSV analysis workflow.

### Testing and deployment

- Automated API tests using `pytest`
- Docker image for reproducible application packaging
- Kubernetes Deployment with two replicas and health probes
- Kubernetes Service for stable access to application Pods
- GitHub Actions workflow to run tests and build the Docker image on pushes and pull requests to `main`

## Tech stack

| Technology | Purpose |
|---|---|
| Python 3.10 | Application logic and CSV analysis |
| FastAPI | HTTP API and request handling |
| Pydantic | Request validation |
| Python `csv` module | CSV parsing and analysis |
| pytest and HTTPX | Automated testing |
| Docker | Containerisation |
| Kubernetes | Deployment, replicas, and health probes |
| GitHub Actions | Continuous integration |

## Getting started

### Prerequisites

- Python 3.10 or compatible version
- pip
- Docker, if running the containerised version
- `kubectl` and a Kubernetes cluster, if deploying to Kubernetes

### 1. Clone the repository

```bash
git clone git@github.com:ShreyaShah108/modelops-lite.git
cd modelops-lite
```

HTTPS can also be used if SSH authentication is not configured.

### 2. Set up the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the tests

```bash
python -m pytest -v
```

### 4. Start the API locally

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open the interactive API documentation at:

`http://127.0.0.1:8000/docs`

Check the health endpoint:

```bash
curl -i http://127.0.0.1:8000/health
```

## Example: Analyse a CSV file

Create a file named `sample.csv`:

```csv
name,age,city
Alice,25,Dublin
Bob,,Cork
Alice,25,Dublin
Charlie,32,Galway
```

Submit the file:

```bash
curl -X POST \
  http://127.0.0.1:8000/analyze-csv \
  -F "file=@sample.csv"
```

Example response:

```json
{
  "filename": "sample.csv",
  "total_rows": 4,
  "total_columns": 3,
  "columns": [
    "name",
    "age",
    "city"
  ],
  "missing_values": {
    "name": 0,
    "age": 1,
    "city": 0
  },
  "duplicate_rows": 1,
  "column_types": {
    "name": "text",
    "age": "numeric",
    "city": "text"
  }
}
```

## Run with Docker

Build the image:

```bash
docker build -t modelops-lite:1.1 .
```

Start the container:

```bash
docker run -d \
  --name modelops-api \
  -p 8000:8000 \
  modelops-lite:1.1
```

Check the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Analyse a CSV:

```bash
curl -X POST \
  http://127.0.0.1:8000/analyze-csv \
  -F "file=@sample.csv"
```

To stop and remove the container:

```bash
docker rm -f modelops-api
```

## Kubernetes deployment

The repository contains Kubernetes manifests under `k8s/` for the application Deployment and Service.

Build the image using the tag expected by your local cluster configuration. For the updated version used during development:

```bash
docker build -t modelops-lite:1.1 .
kubectl set image deployment/modelops-api \
  modelops-api=modelops-lite:1.1
kubectl rollout status deployment/modelops-api
```

Check the Deployment, Pods, and Service:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

Forward local port 8001 to the Service:

```bash
kubectl port-forward service/modelops-service 8001:8000
```

In another terminal, test the API:

```bash
curl http://127.0.0.1:8001/health

curl -X POST \
  http://127.0.0.1:8001/analyze-csv \
  -F "file=@sample.csv"
```

The local Kubernetes cluster must be able to access the locally built image. The provided manifests and image tags should be kept consistent when changing versions.

## Project structure

```text
modelops-lite/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_api.py
├── scripts/
│   ├── run_tests.sh
│   ├── check_health.sh
│   └── validate.sh
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
└── requirements.txt
```

## Engineering and operational considerations

This project was developed as a practical exploration of API development, containerisation, orchestration, and operational troubleshooting.

The implementation includes basic input validation, automated regression tests, container health checks, and Kubernetes deployment management.

The current version is intentionally lightweight:

- CSV analysis runs synchronously within the API request.
- Job metadata is stored in application memory and is lost when the process restarts.
- The data-quality report performs basic checks and type inference, not comprehensive schema validation.
- Upload size is limited, but production deployments would also need appropriate concurrency limits, authentication, and resource controls.
- The Kubernetes configuration is designed for local development and learning rather than production hardening.

## Future improvements

- Persist job records and analysis results in a database.
- Introduce asynchronous processing for larger datasets.
- Add configurable data-quality rules and schema validation.
- Add structured logging and operational metrics.
- Add a frontend for uploading datasets and viewing reports.
- Improve production security, resource limits, and deployment configuration.

## Author

**Shreya Shah**

MSc Computer Science (Data Science), Trinity College Dublin

GitHub: [ShreyaShah108](https://github.com/ShreyaShah108)
