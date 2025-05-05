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
