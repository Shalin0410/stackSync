curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello\")\n    return {\"x\": 42}"}'
