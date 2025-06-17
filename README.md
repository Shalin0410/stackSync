curl -X POST https://safe-python-api-j7yqj4j6la-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    print(\"hello\")\n    return {\"x\": 42}"}'
