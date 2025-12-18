#!/bin/bash

# Get fresh token
curl -s -X POST http://localhost:5002/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@deskringer.com","password":"testpass123"}' > /tmp/token.json

TOKEN=$(cat /tmp/token.json | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "======================================"
echo "Testing DeskRinger Backend - Final Test"
echo "======================================"
echo ""

echo "1. Get Admin Info:"
curl -s http://localhost:5002/api/admin/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "2. Dashboard Stats:"
curl -s http://localhost:5002/api/admin/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "3. Create Customer:"
curl -s -X POST http://localhost:5002/api/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Happy Dental",
    "contact_name": "Dr. Smith",
    "email": "dr.smith@happydental.com",
    "phone": "+14155557890",
    "business_type": "dental",
    "forward_to_number": "+14155557890",
    "greeting_message": "Thank you for calling Happy Dental. How can we help you today?"
  }' | python3 -m json.tool
echo ""

echo "4. Get All Customers:"
curl -s http://localhost:5002/api/customers/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "5. Get Customer #1:"
curl -s http://localhost:5002/api/customers/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "6. Update Customer #1:"
curl -s -X PUT http://localhost:5002/api/customers/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+14155559999"}' | python3 -m json.tool
echo ""

echo "7. Get Recent Calls:"
curl -s "http://localhost:5002/api/calls/recent?limit=5" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "======================================"
echo "All tests complete!"
echo "======================================"
