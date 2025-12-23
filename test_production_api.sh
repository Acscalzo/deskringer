#!/bin/bash

# Test Production API
API_URL="https://deskringer-api.onrender.com"

echo "========================================"
echo "Testing DeskRinger Production API"
echo "========================================"
echo ""

# Test 1: Health Check
echo "1. Health Check:"
curl -s $API_URL/health | python3 -m json.tool
echo ""

# Test 2: API Info
echo "2. API Info:"
curl -s $API_URL/ | python3 -m json.tool
echo ""

# Test 3: Login (replace with your credentials)
echo "3. Admin Login:"
echo "Enter your email:"
read scalzoadam@gmail.com
echo "Enter your password:"
read -s Password_Blue23
echo ""

LOGIN_RESPONSE=$(curl -s -X POST $API_URL/api/admin/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Check your credentials."
    exit 1
fi

echo "✓ Login successful!"
echo ""

# Test 4: Get Admin Info (Protected Endpoint)
echo "4. Get Admin Info (Protected Endpoint):"
curl -s $API_URL/api/admin/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

# Test 5: Dashboard Stats
echo "5. Dashboard Stats:"
curl -s $API_URL/api/admin/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "========================================"
echo "All tests complete!"
echo "========================================"
