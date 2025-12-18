# DeskRinger Backend - Render Deployment Guide

## Step-by-Step Deployment Instructions

### Prerequisites
✅ Backend code pushed to GitHub
✅ GitHub repository: https://github.com/Acscalzo/deskringer

---

## Part 1: Create Render Account

1. **Go to Render**: https://render.com
2. **Sign up** with GitHub (recommended for easy repo access)
3. **Authorize** Render to access your GitHub account
4. You'll be taken to the Render dashboard

---

## Part 2: Create PostgreSQL Database

### Step 1: Create Database
1. In Render dashboard, click **"New +"** button (top right)
2. Select **"PostgreSQL"**
3. Fill in details:
   - **Name**: `deskringer-db`
   - **Database**: `deskringer` (auto-filled)
   - **User**: `deskringer` (auto-filled)
   - **Region**: Choose closest to you (e.g., `Oregon (US West)`)
   - **PostgreSQL Version**: Latest (14 or higher)
   - **Plan**:
     - **Free** (for testing - 90 days free, then $7/month)
     - OR **Starter ($7/month)** - recommended for production
4. Click **"Create Database"**

### Step 2: Wait for Database Creation
- Takes 2-3 minutes
- Status will change from "Creating" to "Available"
- **Don't close this tab!** We'll need info from here

### Step 3: Copy Database URL
1. Once database is "Available", scroll down to **"Connections"** section
2. Find **"Internal Database URL"** (starts with `postgresql://`)
3. Click the **copy icon** to copy the full URL
4. **Save this URL** - we'll need it shortly
5. It looks like: `postgresql://deskringer:PASSWORD@dpg-xxxxx/deskringer`

---

## Part 3: Create Web Service (Flask API)

### Step 1: Create Web Service
1. Click **"New +"** again → **"Web Service"**
2. Click **"Build and deploy from a Git repository"**
3. Click **"Connect a repository"**
4. Find and select: **`Acscalzo/deskringer`**
5. Click **"Connect"**

### Step 2: Configure Web Service
Fill in these settings:

**Basic Settings:**
- **Name**: `deskringer-api` (or whatever you prefer)
- **Region**: Same as your database (e.g., Oregon US West)
- **Branch**: `main`
- **Root Directory**: `backend` ⚠️ **IMPORTANT!**
- **Runtime**: `Python 3`

**Build Settings:**
- **Build Command**: `pip install -r requirements.txt` (auto-detected)
- **Start Command**: `gunicorn app:app` (auto-detected)

**Plan:**
- **Free** (for testing - has sleep after inactivity)
- OR **Starter ($7/month)** - recommended (always on, better performance)

### Step 3: Add Environment Variables
Scroll down to **"Environment Variables"** section and click **"Add Environment Variable"**.

Add these one by one:

```
SECRET_KEY
<click "Generate" button on the right>

JWT_SECRET_KEY
<click "Generate" button on the right>

DATABASE_URL
<paste the PostgreSQL Internal Database URL you copied earlier>

TWILIO_ACCOUNT_SID
<leave blank for now - we'll add later>

TWILIO_AUTH_TOKEN
<leave blank for now>

TWILIO_PHONE_NUMBER
<leave blank for now>

OPENAI_API_KEY
<leave blank for now>

SENDGRID_API_KEY
<leave blank for now>

STRIPE_SECRET_KEY
<leave blank for now>

STRIPE_PUBLISHABLE_KEY
<leave blank for now>
```

**Pro tip:** Click "Generate" for SECRET_KEY and JWT_SECRET_KEY - Render will create secure random values.

### Step 4: Deploy!
1. Scroll to bottom
2. Click **"Create Web Service"**
3. Render will start building and deploying your app
4. This takes 3-5 minutes

### Step 5: Watch the Deployment
- You'll see live logs of the build process
- It will:
  1. Install Python dependencies
  2. Set up the environment
  3. Start Gunicorn
  4. Deploy your app

**Look for:**
```
==> Deploying...
==> Build successful!
==> Your service is live 🎉
```

### Step 6: Copy Your API URL
- Once deployed, you'll see your service URL at the top
- It looks like: `https://deskringer-api.onrender.com`
- **Save this URL!** This is your production API

---

## Part 4: Initialize the Database

Now we need to create the database tables and first admin user.

### Step 1: Open Render Shell
1. In your web service page, click the **"Shell"** tab (top navigation)
2. Click **"Launch Shell"**
3. A terminal will open in your production environment

### Step 2: Create Database Tables
In the shell, run:

```bash
python init_db.py init
```

You should see:
```
Creating database tables...
✓ Database tables created successfully!
```

### Step 3: Create Your First Admin User
In the shell, run (replace with YOUR details):

```bash
python init_db.py create-admin your-email@example.com YourSecurePassword123 "Your Name"
```

Example:
```bash
python init_db.py create-admin adam@deskringer.com MySecurePass123 "Adam Scalzo"
```

You should see:
```
✓ Admin user created successfully!
  Email: adam@deskringer.com
  Name: Adam Scalzo
```

**Save your login credentials!** You'll need these to access the admin dashboard.

### Step 4: Close the Shell
- Type `exit` or just close the terminal window

---

## Part 5: Test Your API

### Test from your computer:

```bash
# Test health check
curl https://deskringer-api.onrender.com/health

# Should return: {"status":"healthy"}

# Test API info
curl https://deskringer-api.onrender.com/

# Should return: {"message":"DeskRinger API","status":"running","version":"1.0.0"}

# Test admin login
curl -X POST https://deskringer-api.onrender.com/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"YourPassword123"}'

# Should return: {"access_token":"eyJ...","admin":{...}}
```

If you see the JSON responses, **your API is live!** 🎉

---

## Part 6: Get Your Database URL for Admin Site

You'll need your API URL for the admin site we'll build next.

**Your Production API URL:**
```
https://deskringer-api.onrender.com
```

**Save this!** The admin dashboard will connect to this URL.

---

## Summary of What You Now Have

✅ **PostgreSQL Database** running on Render
✅ **Flask API** deployed and running
✅ **Database tables** created
✅ **Admin user** created for login
✅ **Live API endpoints** ready to use

**Your URLs:**
- Database: Internal PostgreSQL URL (in Render dashboard)
- API: `https://deskringer-api.onrender.com`

---

## Troubleshooting

### If deployment fails:
1. Check the **"Logs"** tab in Render dashboard
2. Look for errors in red
3. Common issues:
   - Missing environment variables
   - Wrong root directory (should be `backend`)
   - Database URL not set correctly

### If database connection fails:
1. Go to PostgreSQL database in Render
2. Copy the **Internal Database URL** again
3. Update `DATABASE_URL` environment variable in web service
4. Trigger a manual deploy (click "Manual Deploy" → "Deploy latest commit")

### If admin user creation fails:
1. Make sure database tables were created first (`python init_db.py init`)
2. Check if user already exists
3. Look at the error message for clues

---

## Next Steps

1. ✅ Backend API deployed and running
2. 🔜 Build admin dashboard (separate Netlify site)
3. 🔜 Connect admin site to this API
4. 🔜 Add Twilio for phone calls
5. 🔜 Add OpenAI for AI responses
6. 🔜 Add Stripe for payments

---

## Cost Summary

**Current Setup:**
- PostgreSQL: $0 (free for 90 days) then $7/month
- Web Service: $0 (free tier) or $7/month (Starter)

**Total:** $0 now, $7-14/month after free trial

**At $149/month per customer, you break even at just 1 customer!**

---

## Support

If you get stuck:
- Check Render logs (Logs tab)
- Check backend/README.md for more details
- Render docs: https://render.com/docs
