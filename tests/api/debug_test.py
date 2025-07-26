# debug_test.py - Let's see what's actually happening
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'

def debug_registration():
    """Debug the registration endpoint"""
    print("🔍 Debugging registration endpoint...")
    
    test_user_data = {
        'username': f'testuser_{datetime.now().strftime("%H%M%S")}',
        'email': f'test_{datetime.now().strftime("%H%M%S")}@example.com',
        'password': 'testpassword123'
    }
    
    try:
        print(f"📤 Sending POST to: {BASE_URL}/auth/register")
        print(f"📤 Data: {test_user_data}")
        
        response = requests.post(f'{BASE_URL}/auth/register', 
                               json=test_user_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        print(f"📥 Raw Response: {response.text}")
        
        # Try to parse as JSON
        try:
            result = response.json()
            print(f"📥 JSON Response: {result}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            print("📥 Response is not valid JSON")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_other_endpoints():
    """Test some GET endpoints that should work"""
    print("\n🔍 Testing GET endpoints...")
    
    # Test rules chapters
    try:
        response = requests.get(f'{BASE_URL}/rules/core/chapters')
        print(f"📥 Rules chapters: {response.status_code}")
        print(f"📥 Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Rules chapters failed: {e}")
    
    # Test forum posts
    try:
        response = requests.get(f'{BASE_URL}/forum/posts')
        print(f"📥 Forum posts: {response.status_code}")
        print(f"📥 Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Forum posts failed: {e}")

if __name__ == '__main__':
    debug_registration()
    test_other_endpoints()