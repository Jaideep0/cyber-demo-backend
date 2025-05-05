# ─── Stage 1: Build Python packages & install Sherlock ───────────────
FROM python:3.11-slim AS builder

# Install git & certificates, clone Sherlock, install as Python package
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && git clone https://github.com/sherlock-project/sherlock.git /opt/sherlock

WORKDIR /opt/sherlock
RUN pip install --no-cache-dir .

# Install application dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ─── Stage 2: Final runtime image ───────────────────────────────────
FROM python:3.11-slim

# Install CLI demo tools and OpenCV dependencies for steganography
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      exiftool \
      nmap \
      john \
      steghide \
      libgl1-mesa-glx \
      libglib2.0-0 \
      libsm6 \
      libxext6 \
      libxrender1 \
 && rm -rf /var/lib/apt/lists/*

# Copy Python environment (libs & console-scripts)
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and config
WORKDIR /app
COPY app/ ./app
COPY celeryconfig.py .

# Expose FastAPI port
EXPOSE 8000

# Entrypoint: run Uvicorn
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
