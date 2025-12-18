# DeskRinger Backend API

Flask backend for the DeskRinger AI receptionist service.

## Features

- RESTful API for customer and call management
- JWT authentication for admin users
- PostgreSQL database with SQLAlchemy ORM
- Twilio webhooks for phone call handling
- OpenAI integration for AI responses
- Stripe integration for subscription billing
- SendGrid for email notifications

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: JWT tokens (Flask-JWT-Extended)
- **Deployment**: Render
- **Telephony**: Twilio
- **AI**: OpenAI API
- **Payments**: Stripe
- **Email**: SendGrid

## Local Development Setup

### 1. Install Python Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 3. Initialize Database

```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 4. Create Admin User

```bash
# Run Python shell
python3
```

```python
from app import create_app, db
from models import Admin

app = create_app()
with app.app_context():
    admin = Admin(email='admin@deskringer.com', name='Admin User')
    admin.set_password('your-secure-password')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
```

### 5. Run Development Server

```bash
python app.py
```

Server will run at `http://localhost:5000`

## API Endpoints

### Admin Authentication

- `POST /api/admin/login` - Admin login (returns JWT token)
- `GET /api/admin/me` - Get current admin info (requires JWT)
- `POST /api/admin/create` - Create new admin user
- `GET /api/admin/stats` - Get dashboard statistics (requires JWT)

### Customer Management

- `GET /api/customers/` - List all customers (requires JWT)
- `GET /api/customers/<id>` - Get specific customer (requires JWT)
- `POST /api/customers/` - Create new customer (requires JWT)
- `PUT /api/customers/<id>` - Update customer (requires JWT)
- `DELETE /api/customers/<id>` - Cancel customer subscription (requires JWT)
- `PUT /api/customers/<id>/settings` - Update AI settings (requires JWT)

### Call Management

- `GET /api/calls/` - List all calls (requires JWT)
- `GET /api/calls/<id>` - Get specific call details (requires JWT)
- `GET /api/calls/<id>/transcript` - Get call transcript (requires JWT)
- `GET /api/calls/stats` - Get call statistics (requires JWT)
- `GET /api/calls/recent` - Get recent calls (requires JWT)

### Webhooks (No Auth - Called by External Services)

- `POST /api/webhooks/twilio/voice` - Incoming call webhook
- `POST /api/webhooks/twilio/gather` - Speech input processing
- `POST /api/webhooks/twilio/status` - Call status updates
- `POST /api/webhooks/stripe/webhook` - Stripe payment events

### Health Check

- `GET /health` - Health check endpoint
- `GET /` - API info

## Testing the API

### Using curl

```bash
# Login as admin
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@deskringer.com", "password": "your-password"}'

# Get customers (with JWT token)
curl -X GET http://localhost:5000/api/customers/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Using Postman

1. Import the API endpoints into Postman
2. Set up an environment variable for `JWT_TOKEN`
3. Login to get token and save it to the environment
4. Use the token in Authorization header for protected endpoints

## Database Models

### Admin
- Admin users who can access the dashboard
- Email/password authentication

### Customer
- Businesses subscribed to DeskRinger
- Subscription status, billing info, AI settings

### Call
- Individual calls received by the AI
- Call metadata, transcript, summary, costs

### CallLog
- Detailed conversation logs (speaker + message)
- Timestamped entries for each exchange

## Deployment to Render

### 1. Create Render Account

Sign up at https://render.com

### 2. Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `deskringer-db`
3. Select free tier or paid
4. Click "Create Database"
5. Copy the "Internal Database URL" (starts with `postgresql://`)

### 3. Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Settings:
   - **Name**: `deskringer-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free or Starter ($7/month)

### 4. Add Environment Variables

In Render dashboard, add these environment variables:

```
SECRET_KEY=your-secret-key-generate-random-string
JWT_SECRET_KEY=your-jwt-secret-generate-random-string
DATABASE_URL=<paste-from-render-postgres>
TWILIO_ACCOUNT_SID=<from-twilio>
TWILIO_AUTH_TOKEN=<from-twilio>
TWILIO_PHONE_NUMBER=<from-twilio>
OPENAI_API_KEY=<from-openai>
SENDGRID_API_KEY=<from-sendgrid>
STRIPE_SECRET_KEY=<from-stripe>
STRIPE_PUBLISHABLE_KEY=<from-stripe>
```

### 5. Deploy

Render will automatically deploy when you push to your main branch.

Your API will be live at: `https://deskringer-api.onrender.com`

### 6. Run Database Migrations

In Render Shell (available in dashboard):

```bash
flask db upgrade
```

### 7. Create First Admin User

In Render Shell:

```bash
python3
```

```python
from app import create_app, db
from models import Admin

app = create_app()
with app.app_context():
    admin = Admin(email='your-email@example.com', name='Your Name')
    admin.set_password('secure-password')
    db.session.add(admin)
    db.session.commit()
```

## Next Steps

1. ✅ Backend structure complete
2. Set up Twilio account and phone numbers
3. Configure Twilio webhooks to point to your Render URL
4. Integrate OpenAI Realtime API for natural conversations
5. Set up Stripe for payment processing
6. Build admin UI (separate Netlify site)
7. Add notification system (email/SMS)
8. Implement customer onboarding flow

## Cost Breakdown

**Monthly costs (per customer at $149/month):**
- Render Web Service: $7/month (shared across all customers)
- Render PostgreSQL: $7/month (shared across all customers)
- Twilio calls: ~$0.0085/min
- OpenAI API: ~$0.02-0.10/min
- SendGrid: $15/month (shared, up to 40k emails)

**Fixed monthly**: ~$30
**Variable**: ~$0.03-0.11 per minute of calls

With good margins at $149/month per customer!

## Troubleshooting

### Database connection errors
- Verify DATABASE_URL is correct
- Check if PostgreSQL is running (Render dashboard)

### JWT errors
- Ensure JWT_SECRET_KEY is set
- Check token expiration (24 hours default)

### Twilio webhook errors
- Verify webhook URLs in Twilio console
- Check Render logs for errors
- Ensure webhooks are public (no JWT required)

## Support

For issues, check:
1. Render logs (in dashboard)
2. Database connectivity
3. Environment variables are set correctly
