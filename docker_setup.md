# GitScope Backend Docker Setup Guide

This document describes how to build, run, and troubleshoot the containerized FastAPI backend for GitScope.

## Prerequisite
Ensure you have Docker and Docker Desktop installed and running on your system.

---

## 1. Build the Docker Image
To build the Docker image for the backend, execute the following command from the project root directory:

```bash
docker build -t gitscope-backend backend/
```

This command uses the `backend/Dockerfile` to create a lightweight Python 3.12 image and names (tags) it `gitscope-backend`.

---

## 2. Run the Docker Container

To run the container, use the command below. Make sure to adjust the environment variables to match your configuration.

### Important Note on Database URL
When running the application inside a Docker container, **`localhost` or `127.0.0.1` refers to the container itself**, not your host machine. 
- If your PostgreSQL database is running on the host machine, you **must** use **`host.docker.internal`** as the database host so the container can resolve and connect to it.

```bash
docker run -d \
  -p 8000:8000 \
  -e APP_NAME="GitScope" \
  -e APP_VERSION="1.0.0" \
  -e DEBUG="True" \
  -e DATABASE_URL="postgresql+asyncpg://username:password@host.docker.internal:5432/dbName" \
  -e SECRET_KEY="your-secret-key" \
  -e ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="time" \
  -e REFRESH_TOKEN_EXPIRE_DAYS="7" \
  -e GITHUB_TOKEN="your_github_token_here" \
  --name gitscope-backend-container \
  gitscope-backend
```

---

## 3. Useful Commands

### Check Running Containers
To check if the container is running and healthy:
```bash
docker ps
```

### View Application Logs
To view the output or troubleshoot issues:
```bash
docker logs -f gitscope-backend-container
```

### Stop the Container
To stop the running container:
```bash
docker stop gitscope-backend-container
```

### Remove the Container
To remove the stopped container (releasing the name reservation):
```bash
docker rm gitscope-backend-container
```

---

## 4. Troubleshooting

### Port Conflict Error
If you get an error saying port `8000` is already in use, you can either stop the local FastAPI process running on your host or map it to a different host port (e.g. `-p 8080:8000`).

### Container Exits Instantly
If `docker ps` does not show the container running after starting it, check the logs:
```bash
docker logs gitscope-backend-container
```
If you see connection errors related to PostgreSQL, verify that your database server on the host is configured to accept connections from other network interfaces (e.g. checking `listen_addresses = '*'` in your `postgresql.conf` and client authentication rules in `pg_hba.conf`).
