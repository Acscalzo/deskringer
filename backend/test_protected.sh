#!/bin/bash
TOKEN=$(cat /tmp/login_response.json | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Using token: ${TOKEN:0:50}..."
echo ""

echo "=== Testing /api/admin/me ==="
curl -s http://localhost:5002/api/admin/me -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Testing /api/admin/stats ==="
curl -s http://localhost:5002/api/admin/stats -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "=== Testing Create Customer ==="
curl -s -X POST http://localhost:5002/api/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"business_name":"Test Gym","contact_name":"John Doe","email":"john@testgym.com","phone":"+14155556789","business_type":"gym"}' | python3 -m json.tool
echo ""

echo "=== Testing Get Customers ==="
curl -s http://localhost:5002/api/customers/ -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
