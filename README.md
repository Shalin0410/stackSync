# Safe Python Script Execution Service

A service that allows users to execute Python scripts in a secure, sandboxed environment.

## Google Cloud Run API

```bash
curl -X POST https://safe-python-api-j7yqj4j6la-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello\")\n    return {\"x\": 42}"}'
```


## Features

- HTTP API for executing Python scripts
- Secure execution using nsjail sandbox (locally) or Python restrictions (Cloud Run)
- Resource and time limits for script execution
- Support for stdout and return values
- Comprehensive error handling
- Cloud Run compatible with automatic environment detection

## Execution Environments

The service adapts to different execution environments:

1. **Local Development**: Uses nsjail for strong sandboxing
2. **Cloud Run**: Uses Python's built-in security features when nsjail is not available
   
This dual approach ensures the service works reliably across different deployment environments.

## Requirements

- Docker
- Python 3.10+
- nsjail (installed automatically in Docker for local use)

## Installation

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t python-executor .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 python-executor
   ```

## Usage

### API Endpoint

**POST /execute**

Execute a Python script and return the result.

**Request:**
```json
{
  "script": "def main():\n    print('hello')\n    return {'x': 42}"
}
```

**Successful Response:**
```json
{
  "result": {"x": 42},
  "stdout": "hello"
}
```

**Error Response:**
```json
{
  "error": "Script execution failed",
  "message": "division by zero",
  "stdout": "This will fail"
}
```

### Example Usage

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello\")\n    return {\"x\": 42}"}'
```


## Architecture

- **app.py**: Flask application with the HTTP endpoint
- **nsjail.cfg**: Configuration for the nsjail sandbox
- **Dockerfile**: Docker configuration for building the service
