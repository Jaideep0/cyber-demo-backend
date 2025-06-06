# Cyber Demo Monolith

A monolithic Dockerized application for running the Cyber Demo backend services.

## Prerequisites

* [Docker](https://www.docker.com/) (v20.10+ recommended)
* [Docker Compose](https://docs.docker.com/compose/) (v1.29+ recommended)

## Building the Docker Image

To build the Docker image **without using the cache**, run:

```bash
docker build --no-cache -t cyber-demo-monolith:latest .
```

This command:

1. Reads the `Dockerfile` in the current directory.
2. Builds a fresh image named `cyber-demo-monolith:latest`.

## Running the Application with Docker Compose

To build and start all services defined in your `docker-compose.yml`, execute:

```bash
docker-compose build --no-cache
docker-compose up
```

* `docker-compose build --no-cache` will rebuild all images from scratch.
* `docker-compose up` will start the containers and stream their logs.

If you prefer to run in detached mode (in the background), use:

```bash
docker-compose up -d
```

## Manual smoke-tests with curl

1. Manual smoke-tests with curl

### 1.1 Health check

```bash
curl http://localhost:8000/
# → {"message":"Cyber tools backend up!"}
```

### 1.2 Sherlock (sync)

```bash
curl "http://localhost:8000/api/osint/sherlock?username=torvalds"
# → JSON array: [{site, url}, …]
```

### 1.3 Nmap (async)

**Enqueue the scan**

```bash
curl -X POST "http://localhost:8000/api/scan/nmap?target=scanme.nmap.org"
# → {"task_id":"<UUID>"}
```

**Poll for status & result**

```bash
curl "http://localhost:8000/api/status/<UUID>"
# → {"state":"PENDING"} …then eventually…
# → {"state":"SUCCESS","result":{ "22":{…}, "80":{…} }}
```

### 1.4 John‑the‑Ripper Crack Endpoint

```bash
curl -X POST http://localhost:8000/api/crack/john \
  -H "Content-Type: application/json" \
  -d '{"password":"CorrectHorseBatteryStaple123!"}'
```

You should now get back JSON like:

```json
{
  "speed": 50000000.0,
  "keyspace": 916132832,
  "est_time": "18 seconds",
  "feedback": "😬 Weak—will be cracked in seconds."
}
```

This confirms your updated helper is being invoked and you’re seeing real JtR benchmark results.

### 1.5 EXIF-metadata endpoint

```bash
curl -X POST http://localhost:8000/api/exif \
  -F "file=@/path/to/photo.jpg"
```

You should get back a JSON object of all EXIF tags (camera model, timestamps, GPS, etc.).

### 1.6 Steganography Embed/Extract

```bash
curl -X POST http://localhost:8000/api/steg/embed \
  -F "file=@/path/to/input.png" \
  -F "message=Hello world" \
  --output secret.png
```

```bash
curl -X POST http://localhost:8000/api/steg/extract \
  -F "file=@secret.png"
# → {"message":"Hello world"}
```

### 1.7 ARP Scan (netdiscover)

**Enqueue the ARP scan**

```bash
curl -X POST "http://localhost:8000/api/scan/netdiscover?network=192.168.1.0/24"
# → {"task_id":"<UUID>"}
```

**Poll for status & result**

```bash
curl "http://localhost:8000/api/status/<UUID>"
# → {"state":"SUCCESS","result":[{"ip":"192.168.1.10","mac":"aa:bb:cc:..."},…]}
```

### 1.8 Header Analyzer (email header analysis)

**Smoke‑test with curl:**

```bash
curl -X POST http://localhost:8000/api/email/analyze \
  -H "Content-Type: text/plain" \
  --data-binary @test-header.txt
```

You should get back a JSON object:

```json
{
  "From": "alice@example.com",
  "To": "bob@example.org",
  "Subject": "Test Email",
  "Date": "Tue, 5 May 2025 14:23:00 -0400",
  "Message-ID": "<12345@example.com>"
}
```

## Stopping and Cleaning Up

When you're done, you can stop and remove the containers, networks, and volumes with:

```bash
docker-compose down
```

To also remove images created by Compose, add the `--rmi all` flag:

```bash
docker-compose down --rmi all
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
