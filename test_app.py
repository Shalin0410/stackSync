import requests
import json
import unittest

def test_simple_script():
    script = """
def main():
    print("hello")
    return {"x": 42}
"""
    
    response = requests.post(
        "http://localhost:8080/execute",
        json={"script": script},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
def test_error_script():
    script = """
def main():
    print("This will fail")
    return 1/0
"""
    
    response = requests.post(
        "http://localhost:8080/execute",
        json={"script": script},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_no_main_function():
    script = """
print("Hello, but there's no main function")
"""
    
    response = requests.post(
        "http://localhost:8080/execute",
        json={"script": script},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_invalid_json():
    """Test a script that doesn't return JSON-serializable data."""
    script = """
def main():
    class NonSerializable:
        pass
    return NonSerializable()
"""
    response = requests.post(
        "http://localhost:8080/execute",
        json={"script": script},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_missing_script():
    """Test request without a script parameter."""
    response = requests.post(
        "http://localhost:8080/execute",
        json={},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_response_format():
    """Test that the response format matches the requirements"""
    script = """
def main():
    print("hello")
    return {"x": 42}
"""
    response = requests.post(
        "http://localhost:8080/execute",
        json={"script": script},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    data = response.json()
    
    # Check exact keys in response
    print("Response keys:", list(data.keys()))
    print("Response content:", json.dumps(data, indent=2))
    
    # Verify the response has exactly the required keys
    assert set(data.keys()) == {"result", "stdout"}, "Response should have exactly 'result' and 'stdout' keys"
    assert data["result"] == {"x": 42}, "Result should match the return value of main()"
    assert data["stdout"] == "hello", "Stdout should match the print statements"
    
    print("✅ Response format test passed!")

class TestPythonExecutionService(unittest.TestCase):
    BASE_URL = "http://localhost:8080"
    
    def test_simple_script(self):
        """Test a simple script that returns a value."""
        script = """
def main():
    print("hello")
    return {"x": 42}
"""
        response = requests.post(
            f"{self.BASE_URL}/execute",
            json={"script": script},
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"], {"x": 42})
        self.assertIn("hello", data["stdout"])

    def test_response_format(self):
        """Test that the response format matches the exact requirements."""
        script = """
def main():
    print("hello")
    return {"x": 42}
"""
        response = requests.post(
            f"{self.BASE_URL}/execute",
            json={"script": script},
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the response has exactly the required keys and no additional keys
        self.assertEqual(set(data.keys()), {"result", "stdout"}, 
                         "Response should have exactly 'result' and 'stdout' keys")
        
        # Verify the values are correct
        self.assertEqual(data["result"], {"x": 42})
        self.assertEqual(data["stdout"], "hello")

if __name__ == "__main__":
    print("Testing simple script:")
    test_simple_script()
    
    print("\nTesting script with error:")
    test_error_script()
    
    print("\nTesting script without main function:")
    test_no_main_function()
    
    print("\nTesting invalid JSON return:")
    test_invalid_json()
    
    print("\nTesting missing script parameter:")
    test_missing_script()
    
    print("\nTesting response format:")
    test_response_format()
    
    # Uncomment to run unittest tests
    # unittest.main()