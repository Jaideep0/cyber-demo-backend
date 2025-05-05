from fastapi import FastAPI, HTTPException, Query
from fastapi import UploadFile, File, HTTPException
from app.utils.exif import extract_exif_from_bytes
from app.utils.john import get_john_speed, estimate_space, format_seconds, generate_feedback
from app.models import JohnCrackRequest, JohnCrackResult
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

@app.post("/api/exif")
async def exif_endpoint(file: UploadFile = File(...)):
    """
    Upload an image and return its EXIF metadata as JSON.
    """
    data = await file.read()
    try:
        metadata = extract_exif_from_bytes(data)
    except Exception as e:
        raise HTTPException(400, detail=f"Failed to parse EXIF: {e}")
    return metadata

@app.post("/api/crack/john", response_model=JohnCrackResult)
async def crack_with_john(req: JohnCrackRequest):
    """
    Estimate how long John the Ripper would take to brute-force the given password.
    """
    pwd = req.password
    # 1) Benchmark speed
    speed = get_john_speed()
    if speed is None or speed <= 0:
        raise HTTPException(500, detail="Failed to benchmark John the Ripper.")

    # 2) Estimate keyspace
    space = estimate_space(pwd)
    if space == 0:
        raise HTTPException(400, detail="Password must contain valid characters.")

    # 3) Compute time & feedback
    seconds = space / speed
    human = format_seconds(seconds)
    feedback = generate_feedback(seconds)

    return JohnCrackResult(
        speed=speed,
        keyspace=space,
        est_time=human,
        feedback=feedback
    )
