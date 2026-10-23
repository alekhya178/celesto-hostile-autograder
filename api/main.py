import os
import re
from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Hostile Code Autograder Control Plane")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ledger:ledger@ledger:5432/ledger")
SANDBOX_REGEX = re.compile(r"^sbx-[a-z0-9]{8,}$")

class RunState(str, Enum):
    created = "created"
    ready = "ready"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    deleted = "deleted"

class RunCreate(BaseModel):
    run_id: str
    sandbox_name: str
    problem_id: str
    state: str
    execution_target: str

class RunResponse(BaseModel):
    run_id: str
    sandbox_name: str
    problem_id: str
    state: str
    execution_target: str
    created_at: Optional[str] = None

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS runs (
                        run_id VARCHAR(255) PRIMARY KEY,
                        sandbox_name VARCHAR(255) NOT NULL,
                        problem_id VARCHAR(255) NOT NULL,
                        state VARCHAR(50) NOT NULL,
                        execution_target VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    INSERT INTO runs (run_id, sandbox_name, problem_id, state, execution_target)
                    VALUES ('1', 'sbx-seeddemo1', 'demo', 'deleted', 'celesto_sandbox')
                    ON CONFLICT (run_id) DO NOTHING;
                """)
                conn.commit()
    except Exception as e:
        # DB may not be ready during initial module import; will retry on endpoints
        pass

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@app.get("/api/runs", status_code=status.HTTP_200_OK)
def list_runs():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT run_id, sandbox_name, problem_id, state, execution_target, created_at FROM runs ORDER BY created_at ASC")
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "run_id": str(row["run_id"]),
                        "sandbox_name": str(row["sandbox_name"]),
                        "problem_id": str(row["problem_id"]),
                        "state": str(row["state"]),
                        "execution_target": str(row["execution_target"]),
                        "created_at": str(row["created_at"]) if row.get("created_at") else None
                    })
                return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@app.post("/api/runs", status_code=status.HTTP_201_CREATED)
def create_run(run: RunCreate):
    # Strict validation rules
    if run.execution_target != "celesto_sandbox":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="execution_target must be exactly 'celesto_sandbox'"
        )

    if not SANDBOX_REGEX.match(run.sandbox_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sandbox_name must match pattern '^sbx-[a-z0-9]{8,}$'"
        )

    valid_states = {s.value for s in RunState}
    if run.state not in valid_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"state must be one of {valid_states}"
        )

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO runs (run_id, sandbox_name, problem_id, state, execution_target)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                        sandbox_name = EXCLUDED.sandbox_name,
                        problem_id = EXCLUDED.problem_id,
                        state = EXCLUDED.state,
                        execution_target = EXCLUDED.execution_target
                    RETURNING run_id, sandbox_name, problem_id, state, execution_target, created_at;
                """, (run.run_id, run.sandbox_name, run.problem_id, run.state, run.execution_target))
                created = cur.fetchone()
                conn.commit()
                return {
                    "run_id": str(created["run_id"]),
                    "sandbox_name": str(created["sandbox_name"]),
                    "problem_id": str(created["problem_id"]),
                    "state": str(created["state"]),
                    "execution_target": str(created["execution_target"]),
                    "created_at": str(created["created_at"]) if created.get("created_at") else None
                }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insert error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("API_PORT", "8080")), reload=False)
