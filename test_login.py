#!/usr/bin/env python3
import urllib.request
import urllib.error
import json

API_URL = "https://deskringer-api.onrender.com"

print("=" * 50)
print("Testing DeskRinger Production API")
print("=" * 50)
print()

# Test 1: Health Check
print("1. Health Check:")
response = urllib.request.urlopen(f"{API_URL}/health")
data = json.loads(response.read())
print(json.dumps(data, indent=2))
print()

# Test 2: API Info
print("2. API Info:")
response = urllib.request.urlopen(f"{API_URL}/")
data = json.loads(response.read())
print(json.dumps(data, indent=2))
print()

# Test 3: Admin Login
print("3. Admin Login:")
login_data = {
    "email": "scalzoadam@gmail.com",
    "password": "Password_Blue23"
}
req = urllib.request.Request(
    f"{API_URL}/api/admin/login",
    data=json.dumps(login_data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    print(json.dumps(data, indent=2))
    print()

    if 'access_token' in data:
        token = data['access_token']
        print("✓ Login successful!")
        print(f"Token: {token[:50]}...")
        print()

        # Test 4: Get Admin Info (Protected)
        print("4. Get Admin Info (Protected Endpoint):")
        req = urllib.request.Request(
            f"{API_URL}/api/admin/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        print(json.dumps(data, indent=2))
        print()

        # Test 5: Dashboard Stats
        print("5. Dashboard Stats:")
        req = urllib.request.Request(
            f"{API_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        print(json.dumps(data, indent=2))
        print()
    else:
        print("❌ Login failed!")
        print()
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
    print(e.read().decode())
    print()

print("=" * 50)
print("Tests Complete!")
print("=" * 50)
