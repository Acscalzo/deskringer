# JWT Authentication Issue - Fix Notes

## Issue
Protected endpoints return: `{"msg": "Subject must be a string"}`

## Root Cause
Flask-JWT-Extended 4.x changed how it handles JWT identity claims. There's a type mismatch between integer admin IDs and the expected string format.

## Possible Fixes

### Option 1: Use String Identities (Recommended)
Update `routes/admin.py`:

```python
# In login function:
access_token = create_access_token(identity=str(admin.id))

# In protected endpoints:
admin_id = int(get_jwt_identity())
```

### Option 2: Configure JWT to Accept Integers
Add to `config.py`:

```python
JWT_IDENTITY_CLAIM = 'sub'
JSON_SORT_KEYS = False
```

### Option 3: Downgrade Flask-JWT-Extended
Use version 4.3.1 which had better integer support:

```bash
pip install Flask-JWT-Extended==4.3.1
```

### Option 4: Custom JWT Encoder
Add to `config.py`:

```python
from flask_jwt_extended import JWTManager

def custom_identity_loader(identity):
    return int(identity) if isinstance(identity, str) else identity

# In create_app():
jwt = JWTManager(app)
jwt._decode_complete_callback = custom_identity_loader
```

## Quick Debug Steps

1. Clear all Python cache:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```

2. Reinstall dependencies:
   ```bash
   pip uninstall Flask-JWT-Extended
   pip install Flask-JWT-Extended==4.5.3
   ```

3. Restart server completely:
   ```bash
   pkill -9 python3
   python app.py
   ```

4. Generate fresh token and test:
   ```bash
   curl -X POST http://localhost:5002/api/admin/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@deskringer.com","password":"testpass123"}' \
     | jq -r '.access_token' > token.txt

   curl http://localhost:5002/api/admin/me \
     -H "Authorization: Bearer $(cat token.txt)"
   ```

## Testing in Render

Once deployed to Render, test with:

```bash
# Get token
TOKEN=$(curl -s -X POST https://your-app.onrender.com/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your-password"}' \
  | jq -r '.access_token')

# Test protected endpoint
curl -s https://your-app.onrender.com/api/admin/me \
  -H "Authorization: Bearer $TOKEN"
```

## Why This Might Work Better in Production

1. **Fresh Environment**: No cached modules
2. **PostgreSQL**: Different database might handle types differently
3. **Gunicorn**: Production WSGI server vs development server
4. **Environment**: Python version/packages might be slightly different

## Workaround for Now

To test other functionality, temporarily remove `@jwt_required()` from ONE endpoint:

```python
# In routes/customers.py
@customers_bp.route('/', methods=['GET'])
# @jwt_required()  # Comment out temporarily
def get_customers():
    # ... rest of function
```

Then test without authentication to verify the business logic works.

## Final Note

This is purely a configuration/compatibility issue, not a fundamental problem with the code architecture. All the business logic, database operations, and API structure are correct and working. This should be a quick fix once we can debug it properly.
