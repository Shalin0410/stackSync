# Safe Python Script Execution Service

A service that allows users to execute Python scripts in a secure, sandboxed environment.

Completion Time: 2hrs

## Google Cloud Run API

```bash
curl -X POST https://safe-python-api-j7yqj4j6la-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello from cloud\")\n    return {\"x\": 42}"}'
```

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


### Example Usage

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello\")\n    return {\"x\": 42}"}'
```
