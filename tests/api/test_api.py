# test_api.py - Comprehensive API testing script
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api/v1'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_data = {
            'username': f'testuser_{datetime.now().strftime("%H%M%S")}',
            'email': f'test_{datetime.now().strftime("%H%M%S")}@example.com',
            'password': 'testpassword123'
        }
        
    def test_health_check(self):
        """Test the health endpoint"""
        print("🔍 Testing health check...")
        try:
            response = requests.get('http://localhost:5000/api/health')
            print(f"✅ Health check: {response.status_code} - {response.json()}")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_registration(self):
        """Test user registration"""
        print("\n🔍 Testing user registration...")
        try:
            response = self.session.post(f'{BASE_URL}/auth/register', 
                                       json=self.test_user_data)
            result = response.json()
            print(f"✅ Registration: {response.status_code} - {result.get('message', 'Success')}")
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def test_login(self):
        """Test user login"""
        print("\n🔍 Testing user login...")
        try:
            login_data = {
                'email': self.test_user_data['email'],
                'password': self.test_user_data['password']
            }
            response = self.session.post(f'{BASE_URL}/auth/login', json=login_data)
            result = response.json()
            print(f"✅ Login: {response.status_code} - {result.get('message', 'Success')}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def test_current_user(self):
        """Test getting current user"""
        print("\n🔍 Testing current user endpoint...")
        try:
            response = self.session.get(f'{BASE_URL}/auth/me')
            result = response.json()
            print(f"✅ Current user: {response.status_code} - User: {result.get('data', {}).get('username', 'Unknown')}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Current user failed: {e}")
            return False
    
    def test_rules_endpoints(self):
        """Test rules API endpoints"""
        print("\n🔍 Testing rules endpoints...")
        
        # Test chapters
        try:
            response = self.session.get(f'{BASE_URL}/rules/core/chapters')
            print(f"✅ Core chapters: {response.status_code}")
        except Exception as e:
            print(f"❌ Core chapters failed: {e}")
        
        # Test sections list
        try:
            response = self.session.get(f'{BASE_URL}/rules/sections')
            result = response.json()
            section_count = len(result.get('data', {}).get('sections', []))
            print(f"✅ Sections list: {response.status_code} - {section_count} sections found")
        except Exception as e:
            print(f"❌ Sections list failed: {e}")
        
        # Test search
        try:
            response = self.session.get(f'{BASE_URL}/rules/search?q=magic')
            result = response.json()
            search_count = result.get('data', {}).get('count', 0)
            print(f"✅ Rules search: {response.status_code} - {search_count} results")
        except Exception as e:
            print(f"❌ Rules search failed: {e}")
    
    def test_forum_endpoints(self):
        """Test forum API endpoints"""
        print("\n🔍 Testing forum endpoints...")
        
        # Test getting posts
        try:
            response = self.session.get(f'{BASE_URL}/forum/posts')
            result = response.json()
            post_count = len(result.get('data', {}).get('posts', []))
            print(f"✅ Forum posts: {response.status_code} - {post_count} posts found")
        except Exception as e:
            print(f"❌ Forum posts failed: {e}")
        
        # Test creating a post
        try:
            post_data = {
                'title': 'Test Post from API',
                'content': 'This is a test post created via the API testing script.'
            }
            response = self.session.post(f'{BASE_URL}/forum/posts/create', json=post_data)
            result = response.json()
            if response.status_code == 201:
                post_id = result.get('data', {}).get('id')
                print(f"✅ Create post: {response.status_code} - Post ID: {post_id}")
                return post_id
            else:
                print(f"⚠️ Create post: {response.status_code} - {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Create post failed: {e}")
        
        return None
    
    def test_user_profile(self):
        """Test user profile endpoints"""
        print("\n🔍 Testing user profile...")
        try:
            response = self.session.get(f'{BASE_URL}/users/profile')
            result = response.json()
            username = result.get('data', {}).get('username', 'Unknown')
            print(f"✅ User profile: {response.status_code} - Username: {username}")
        except Exception as e:
            print(f"❌ User profile failed: {e}")
    
    def test_logout(self):
        """Test user logout"""
        print("\n🔍 Testing logout...")
        try:
            response = self.session.post(f'{BASE_URL}/auth/logout')
            result = response.json()
            print(f"✅ Logout: {response.status_code} - {result.get('message', 'Success')}")
        except Exception as e:
            print(f"❌ Logout failed: {e}")
    
    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting comprehensive API tests...\n")
        
        # Test sequence
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return
        
        if not self.test_registration():
            print("❌ Registration failed - stopping tests")
            return
        
        if not self.test_login():
            print("❌ Login failed - stopping tests")
            return
        
        self.test_current_user()
        self.test_rules_endpoints()
        post_id = self.test_forum_endpoints()
        self.test_user_profile()
        self.test_logout()
        
        print("\n🎉 API tests completed!")
        print(f"📝 Test user created: {self.test_user_data['email']}")
        if post_id:
            print(f"📝 Test post created with ID: {post_id}")

if __name__ == '__main__':
    print("🧪 LotusRPG API Test Suite")
    print("=" * 50)
    
    tester = APITester()
    tester.run_all_tests()