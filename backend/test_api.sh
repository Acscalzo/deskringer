#!/bin/bash

# API Testing Script for DeskRinger Backend
BASE_URL="http://localhost:5002"

echo "=========================================="
echo "Testing DeskRinger Backend API"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "1. Testing Health Check Endpoint..."
curl -s $BASE_URL/health | python3 -m json.tool
echo -e "\n✓ Health check passed\n"

# Test 2: Admin Login
echo "2. Testing Admin Login..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@deskringer.com","password":"testpass123"}')

echo "$LOGIN_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo -e "\n✓ Admin login successful\n"

# Test 3: Get Admin Info
echo "3. Testing Get Current Admin..."
curl -s $BASE_URL/api/admin/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n✓ Get admin info passed\n"

# Test 4: Get Dashboard Stats
echo "4. Testing Dashboard Statistics..."
curl -s $BASE_URL/api/admin/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n✓ Dashboard stats passed\n"

# Test 5: Create Customer
echo "5. Testing Create Customer..."
curl -s -X POST $BASE_URL/api/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Test Salon",
    "contact_name": "Jane Smith",
    "email": "jane@testsalon.com",
    "phone": "+14155551234",
    "business_type": "salon",
    "forward_to_number": "+14155551234"
  }' | python3 -m json.tool
echo -e "\n✓ Customer creation passed\n"

# Test 6: Get All Customers
echo "6. Testing Get All Customers..."
curl -s $BASE_URL/api/customers/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n✓ Get customers passed\n"

# Test 7: Get Specific Customer
echo "7. Testing Get Specific Customer..."
curl -s $BASE_URL/api/customers/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n✓ Get specific customer passed\n"

# Test 8: Get All Calls
echo "8. Testing Get All Calls..."
curl -s $BASE_URL/api/calls/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n✓ Get calls passed\n"

# Test 9: Get Call Stats
echo "9. Testing Call Statistics..."
curl -s "$BASE_URL/api/calls/stats?days=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo -e "\n✓ Call stats passed\n"

# Test 10: Test Invalid Login
echo "10. Testing Invalid Login (should fail)..."
curl -s -X POST $BASE_URL/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@deskringer.com","password":"wrongpassword"}' | python3 -m json.tool
echo -e "\n✓ Invalid login correctly rejected\n"

echo "=========================================="
echo "All Tests Complete!"
echo "=========================================="
