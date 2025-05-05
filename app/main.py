from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Any
from celery.result import AsyncResult
from app.models import SherlockResult  # your Pydantic model
from app.tasks import scan_nmap
import subprocess

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Cyber tools backend up!"}

# ————————————————————————————————————————————————
# Sherlock (sync) lookup
@app.get("/api/osint/sherlock", response_model=List[SherlockResult])
async def osint_sherlock(
    username: str = Query(..., description="Username to search"),
    timeout: int = Query(5, ge=1, description="Timeout per site")
):
    cmd = ["sherlock", username, "--timeout", str(timeout), "--print-found"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, detail=e.stderr.strip())

    results = []
    for line in proc.stdout.splitlines():
        if line.startswith("[+]"):
            site, url = line[3:].strip().split(": ", 1)
            results.append(SherlockResult(site=site, url=url))
    return results

# ————————————————————————————————————————————————
# Nmap scan (async via Celery)
@app.post("/api/scan/nmap")
async def enqueue_nmap(target: str = Query(..., description="Host or IP to scan")):
    task = scan_nmap.delay(target)
    return {"task_id": task.id}

# Task status endpoint
@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    result = AsyncResult(task_id, app=scan_nmap.app)
    if result.state == "PENDING":
        # No such task yet
        return {"state": result.state}
    if result.state == "SUCCESS":
        return {"state": result.state, "result": result.result}
    if result.state == "FAILURE":
        # You can include traceback via result.result
        return JSONResponse(
            status_code=500,
            content={"state": result.state, "error": str(result.result)},
        )
    # other states: STARTED, RETRY, etc.
    return {"state": result.state}
