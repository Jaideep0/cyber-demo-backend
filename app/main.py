from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
import subprocess
import io
from celery.result import AsyncResult
from app.models import SherlockResult, JohnCrackRequest, JohnCrackResult
from app.tasks import scan_nmap, scan_netdiscover
from app.utils.exif import extract_exif_from_bytes
from app.utils.password import score_password
from app.utils.john import get_john_speed, estimate_space, format_seconds, generate_feedback
from app.utils.steg import embed_message, extract_message
from app.utils.email import parse_email_headers

app = FastAPI()

origins = ["*"]

# app.add_middleware(
#   CORSMiddleware,
#   allow_origins=["http://localhost:3000"],  # your frontend origin
#   allow_credentials=True,
#   allow_methods=["*"],
#   allow_headers=["*"],
# )

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,  # your frontend origin
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Cyber tools backend up!"}

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

@app.post("/api/scan/nmap")
async def enqueue_nmap(target: str = Query(..., description="Host or IP to scan")):
    task = scan_nmap.delay(target)
    return {"task_id": task.id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    result = AsyncResult(task_id, app=scan_nmap.app)
    if result.state == "PENDING":
        return {"state": result.state}
    if result.state == "SUCCESS":
        return {"state": result.state, "result": result.result}
    if result.state == "FAILURE":
        return JSONResponse(status_code=500, content={"state": result.state, "error": str(result.result)})
    return {"state": result.state}

@app.post("/api/exif")
async def exif_endpoint(file: UploadFile = File(...)):
    data = await file.read()
    try:
        metadata = extract_exif_from_bytes(data)
    except Exception as e:
        raise HTTPException(400, detail=f"Failed to parse EXIF: {e}")
    return metadata

@app.get("/api/password-strength")
async def password_strength(pwd: str = Query(..., description="Password to evaluate")):
    analysis = score_password(pwd)
    return analysis

@app.post("/api/crack/john", response_model=JohnCrackResult)
async def crack_with_john(req: JohnCrackRequest):
    pwd = req.password
    speed = get_john_speed()
    if speed is None or speed <= 0:
        raise HTTPException(500, detail="Failed to benchmark John the Ripper.")
    space = estimate_space(pwd)
    if space == 0:
        raise HTTPException(400, detail="Password must contain valid characters.")
    seconds = space / speed
    human = format_seconds(seconds)
    feedback = generate_feedback(seconds)
    return JohnCrackResult(speed=speed, keyspace=space, est_time=human, feedback=feedback)

@app.post("/api/steg/embed")
async def steg_embed(
    file: UploadFile = File(...),
    message: str = Form(..., description="Text to hide")
):
    data = await file.read()
    try:
        png_bytes = embed_message(data, message)
    except Exception as e:
        raise HTTPException(400, detail=f"Embedding failed: {e}")
    return StreamingResponse(
        io.BytesIO(png_bytes),
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=secret.png"}
    )

@app.post("/api/steg/extract")
async def steg_extract(file: UploadFile = File(...)):
    data = await file.read()
    try:
        msg = extract_message(data)
    except Exception as e:
        raise HTTPException(400, detail=f"Extraction failed: {e}")
    return {"message": msg}

@app.post("/api/scan/netdiscover")
async def enqueue_netdiscover(
    network: str = Query(..., description="CIDR to scan, e.g. 192.168.1.0/24")
):
    task = scan_netdiscover.delay(network)
    return {"task_id": task.id}

@app.post("/api/email/analyze")
async def analyze_email(header: str = Body(..., description="Raw email headers")):
    try:
        data = parse_email_headers(header)
    except Exception as e:
        raise HTTPException(400, detail=f"Failed to parse headers: {e}")
    return data