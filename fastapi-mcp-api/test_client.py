import requests
import json

# Base URL for your FastAPI app
BASE_URL = "http://localhost:8888"

def test_create_greeting():
    """Test the create_greeting endpoint with different parameters sent via request body."""
    
    # Test 1: Basic greeting in English (default)
    print("=== Test 1: Basic English greeting ===")
    response = requests.post(f"{BASE_URL}/api/greeting", 
                           json={"name": "Alice"},
                           headers={"Content-Type": "application/json"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test 2: Spanish greeting
    print("=== Test 2: Spanish greeting ===")
    response = requests.post(f"{BASE_URL}/api/greeting", 
                           json={"name": "Carlos", "language": "spanish"},
                           headers={"Content-Type": "application/json"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test 3: French greeting
    print("=== Test 3: French greeting ===")
    response = requests.post(f"{BASE_URL}/api/greeting", 
                           json={"name": "Marie", "language": "french"},
                           headers={"Content-Type": "application/json"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test 4: German greeting
    print("=== Test 4: German greeting ===")
    response = requests.post(f"{BASE_URL}/api/greeting", 
                           json={"name": "Klaus", "language": "german"},
                           headers={"Content-Type": "application/json"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test 5: Unsupported language (falls back to English)
    print("=== Test 5: Unsupported language ===")
    response = requests.post(f"{BASE_URL}/api/greeting", 
                           json={"name": "Yuki", "language": "japanese"},
                           headers={"Content-Type": "application/json"})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    try:
        test_create_greeting()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure your FastAPI app is running on http://localhost:8888")
        print("Run: python app.py")
    except Exception as e:
        print(f"An error occurred: {e}") 