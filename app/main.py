
import csv
import io
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

app = FastAPI(title="ModelOps Lite")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class JobCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    simulate_failure: bool = False


jobs: dict[str, dict] = {}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return health status of API."""
    return {"status": "okay"}


@app.post("/jobs", status_code=201)
def create_job(request: JobCreate) -> dict:
    job_id = str(uuid4())
    status = "failed" if request.simulate_failure else "completed"

    job = {
        "id": job_id,
        "name": request.name,
        "status": status,
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


@app.post("/analyze-csv")
async def analyze_csv(file: UploadFile = File(...)) -> dict:
    """Analyze a CSV file and return a basic data-quality report."""

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 5 MB size limit.",
        )

    try:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        if not reader.fieldnames or any(
            not name.strip() for name in reader.fieldnames
        ):
            raise HTTPException(
                status_code=400,
                detail="CSV must contain non-empty column headers.",
            )

        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise HTTPException(
                status_code=400,
                detail="CSV column names must be unique.",
            )

        columns = reader.fieldnames
        rows = list(reader)

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must use UTF-8 text encoding.",
        )
    except csv.Error:
        raise HTTPException(
            status_code=400,
            detail="Could not parse the CSV file.",
        )

    # Count missing values in each column.
    missing_values = {
        column: sum(
            1
            for row in rows
            if row.get(column) is None or not row[column].strip()
        )
        for column in columns
    }

    # Count repeated rows, excluding the first occurrence.
    seen_rows = set()
    duplicate_rows = 0

    for row in rows:
        row_values = tuple(row.get(column, "") for column in columns)

        if row_values in seen_rows:
            duplicate_rows += 1
        else:
            seen_rows.add(row_values)

    # Infer a basic type for each column.
    column_types = {}

    for column in columns:
        values = [
            row[column].strip()
            for row in rows
            if row.get(column) is not None and row[column].strip()
        ]

        if values and all(is_number(value) for value in values):
            column_types[column] = "numeric"
        else:
            column_types[column] = "text"

    return {
        "filename": file.filename,
        "total_rows": len(rows),
        "total_columns": len(columns),
        "columns": columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "column_types": column_types,
    }


def is_number(value: str) -> bool:
    """Return whether a string can be interpreted as a number."""
    try:
        float(value)
        return True
    except ValueError:
        return False
