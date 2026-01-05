# DeskRinger Customer Portal

Customer-facing portal where businesses can view calls, manage settings, and handle their DeskRinger account.

## Features

- **Call Feed** - View all calls with AI summaries
- **Call Details** - Full transcripts and conversation history
- **Mark as Handled** - Track which calls have been addressed
- **Settings** - Update business info, AI greeting, and instructions
- **Password Management** - Change portal password

## Deployment to Netlify

### 1. Create New Site

1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect to your GitHub repository
4. Configure:
   - **Branch:** main
   - **Base directory:** customer-app
   - **Publish directory:** (leave empty or use `.`)
5. Click "Deploy site"

### 2. Set Up Custom Domain

1. In Netlify dashboard → Domain settings
2. Add custom domain: `app.deskringer.com`
3. Configure DNS in your domain registrar:
   - Add CNAME record: `app` → your-site.netlify.app
4. Netlify will automatically provision SSL certificate

### 3. Run Database Migration

The backend needs new fields in the database. Run this SQL on your Render PostgreSQL database:

```sql
-- Add password and last_login to customers
ALTER TABLE customers
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- Add handled tracking to calls
ALTER TABLE calls
ADD COLUMN IF NOT EXISTS handled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS handled_at TIMESTAMP;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_calls_handled ON calls(handled);
CREATE INDEX IF NOT EXISTS idx_calls_customer_created ON calls(customer_id, created_at DESC);
```

**To run on Render:**
1. Go to your PostgreSQL database in Render dashboard
2. Click "Connect" → "External Connection"
3. Use the connection string with a PostgreSQL client (like psql or TablePlus)
4. Run the SQL above

### 4. Set Customer Passwords

Existing customers won't have passwords yet. You need to set them via the admin dashboard:

**Option A - Update via API:**
```python
# In Render shell or locally
from app import create_app, db
from models import Customer

app = create_app()
with app.app_context():
    customer = Customer.query.filter_by(email='customer@example.com').first()
    customer.set_password('temporaryPassword123')
    db.session.commit()
    print(f"Password set for {customer.email}")
```

**Option B - Add to admin dashboard:**
We should add a "Set Password" button in the admin customer management page later.

### 5. Test the Portal

1. Go to https://app.deskringer.com
2. Login with customer email and password
3. You should see the dashboard with call feed

## Backend API Endpoints

All customer portal endpoints are under `/api/portal/`:

- `POST /api/portal/login` - Customer login
- `GET /api/portal/me` - Get customer info
- `GET /api/portal/stats` - Get call statistics
- `GET /api/portal/calls` - Get customer's calls
- `GET /api/portal/calls/:id` - Get call details with transcript
- `POST /api/portal/calls/:id/mark-handled` - Mark call as handled
- `POST /api/portal/calls/:id/mark-unhandled` - Mark call as unhandled
- `PUT /api/portal/settings` - Update customer settings
- `POST /api/portal/change-password` - Change password

## Local Testing

1. Update `customer-app/js/config.js` to use localhost:
   ```javascript
   const API_BASE_URL = 'http://localhost:5000';
   ```

2. Open `customer-app/index.html` in a browser
3. Make sure backend is running locally

## Next Steps

### Immediate:
1. Deploy to Netlify as `app.deskringer.com`
2. Run database migration on production
3. Set passwords for existing customers
4. Test with a real customer

### Future Enhancements:
- Add "Set Customer Password" button in admin dashboard
- Email customers invite to portal (with temporary password)
- Add call analytics/insights
- Add calendar integration for appointments
- Add webhook settings for CRM integration
- Add SMS/Email notification toggles
- Export call history to CSV
