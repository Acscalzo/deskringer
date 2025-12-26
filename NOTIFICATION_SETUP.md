# Notification System Setup Guide

This guide will help you set up email and SMS notifications so business owners get alerted after every call.

---

## Overview

When a call completes:
1. System generates a summary of the call
2. **Email** sent with full transcript + summary (if notification_email is set)
3. **SMS** sent with brief summary (if notification_phone is set)
4. Notifications customized based on notification_instructions for each business

---

## Step 1: Add Database Columns

The notification fields need to be added to the database.

### Via Render Shell:

1. Go to https://dashboard.render.com
2. Select **deskringer-api** service
3. Click **"Shell"** tab (left sidebar)
4. Paste this command:

```bash
python3 -c '
from app import create_app
from models import db
app = create_app()
app.app_context().push()
from sqlalchemy import text

# Add notification columns
db.session.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS notification_email VARCHAR(120)"))
db.session.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS notification_phone VARCHAR(20)"))
db.session.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS notification_instructions TEXT"))

db.session.commit()
print("✅ Notification columns added successfully!")
'
```

5. Hit Enter and wait for "✅ Notification columns added successfully!"

---

## Step 2: Set Up SendGrid (Email)

### Create SendGrid Account:

1. Go to https://sendgrid.com/
2. Sign up for free account (100 emails/day free forever)
3. Verify your email address

### Get API Key:

1. Go to **Settings** → **API Keys** (https://app.sendgrid.com/settings/api_keys)
2. Click **"Create API Key"**
3. Name: "DeskRinger Notifications"
4. **Permissions:** Full Access (or just "Mail Send")
5. Click **"Create & View"**
6. **Copy the API key** (starts with `SG.`)
   - You can only see this once! Save it somewhere safe

### Verify Sender Email (Important!):

1. Go to **Settings** → **Sender Authentication** (https://app.sendgrid.com/settings/sender_auth)
2. Click **"Verify a Single Sender"**
3. Fill in form:
   - From Name: "DeskRinger Notifications"
   - From Email: your email (e.g., notifications@yourdomain.com or your personal email)
   - Reply To: same email
   - Company Address: your info
4. Click **"Create"**
5. Check your email and click verification link
6. Once verified, this email can send notifications!

---

## Step 3: Add Environment Variables to Render

1. Go to https://dashboard.render.com
2. Select **deskringer-api** service
3. Click **"Environment"** tab
4. Add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SENDGRID_API_KEY` | `SG.xxxxxxxxxxxxx` | From Step 2 |
| `NOTIFICATION_FROM_EMAIL` | `notifications@yourdomain.com` | The verified sender email from Step 2 |
| `TWILIO_PHONE_NUMBER` | `+19085032782` | Your Twilio number (for SMS) |

**Note:** `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` should already be set from earlier!

5. Click **"Save Changes"**
6. Render will auto-redeploy (2-3 mins)

---

## Step 4: Deploy Frontend

The admin dashboard needs to be deployed with the new notification fields:

1. Go to https://app.netlify.com
2. Select **deskringer-admin** site
3. **Deploys** tab → **"Trigger deploy"** → **"Deploy site"**
4. Wait for deployment to finish

---

## Step 5: Configure Notifications for a Customer

1. Go to admin dashboard: https://admin.deskringer.com
2. Edit a customer (e.g., Aatrox's Pizza Shop)
3. Scroll down to **"📧 Notification Settings"**
4. Fill in:
   - **Notification Email:** Where to send email alerts (e.g., owner@pizzashop.com)
   - **Notification Phone:** Where to send SMS (e.g., +1234567890) - optional
   - **Notification Instructions:** Custom formatting for this business

### Example Notification Instructions:

**For Pizza Shop:**
```
When summarizing calls, make sure to include:
- Type of pizza ordered
- Size and toppings
- Pickup or delivery
- Requested time
- Customer name and callback number

Format as: "[Customer Name] wants [Order Details] for [Pickup/Delivery] at [Time]"
```

**For Salon:**
```
When summarizing calls, make sure to include:
- Service requested (haircut, color, nails, etc.)
- Preferred stylist (if mentioned)
- Preferred date/time
- Customer name and phone

Format as: "[Customer Name] wants [Service] with [Stylist] on [Date/Time]"
```

**For HVAC:**
```
When summarizing calls, include:
- Type of issue (no heat, AC broken, maintenance, etc.)
- Urgency level
- Property address (if mentioned)
- Customer name and callback number

Format as: "URGENT: [Issue] at [Address] - Call [Customer] at [Phone]"
```

5. Click **"Save Customer"**

---

## Step 6: Test Notifications

### Test Email Notification:

1. Call your DeskRinger number: **+1 908 503 2782**
2. Have a conversation with the AI
3. Hang up
4. Within 1-2 minutes, check the notification email inbox
5. You should receive:
   - **Subject:** "New call from [caller] - [Business Name]"
   - **Body:** Full transcript, summary, call details
   - Beautiful HTML formatting

### Test SMS Notification:

1. Make sure `notification_phone` is set for the customer
2. Call the number again
3. Hang up
4. Within 1-2 minutes, check the notification phone
5. You should receive an SMS with brief summary

---

## How It Works

### Email Template Features:

- 📞 **Call Summary Card:** Caller info, duration, status
- ⚠️ **Special Instructions:** Shows notification_instructions if set
- 💬 **AI Summary:** Quick overview of what caller wanted
- 📝 **Full Transcript:** Complete conversation
- 🔗 **View in Dashboard:** Link to admin portal

### SMS Template:

- **Short format** (fits in 1-2 messages)
- Caller name/number
- Brief summary
- Link to dashboard

---

## Troubleshooting

### Emails Not Sending:

1. **Check Render logs:** Look for "Email notification sent" or errors
2. **Verify SendGrid API key** is correct in Render env vars
3. **Check sender verification:** Make sure the `NOTIFICATION_FROM_EMAIL` is verified in SendGrid
4. **Check spam folder:** SendGrid emails might go to spam initially
5. **SendGrid dashboard:** Check activity log at https://app.sendgrid.com/email_activity

### SMS Not Sending:

1. **Check Render logs:** Look for "SMS notification sent" or errors
2. **Verify phone format:** Must be E.164 format (+1234567890)
3. **Twilio verification:** On trial account, receiving numbers must be verified
4. **Check Twilio logs:** https://console.twilio.com/monitor/logs/sms

### Notifications Not Triggering:

1. **Check call status:** Only sends for "completed" calls
2. **Check webhook:** Make sure Twilio status callback is configured
3. **Check notification settings:** Verify notification_email or notification_phone is set
4. **Check Render logs:** Look for "Notifications sent for call X"

---

## Costs

### SendGrid:
- **Free tier:** 100 emails/day forever (enough for 3,000/month)
- **Pro plan:** $19.95/month for 50,000 emails

### Twilio SMS:
- **Cost:** ~$0.0079 per SMS sent
- **Example:** 100 SMS/month = $0.79

**For most customers, email is enough. SMS is optional for urgent alerts.**

---

## Next Steps

Once notifications are working:

1. **Test with real call:** Have someone call your test number
2. **Verify formatting:** Make sure notifications look good
3. **Customize per business:** Add specific instructions for each customer type
4. **Launch!** Now business owners get instant alerts

---

## Example Notification Email

Here's what business owners will receive:

```
From: DeskRinger Notifications <notifications@deskringer.com>
To: owner@pizzashop.com
Subject: New call from (555) 123-4567 - Aatrox's Pizza Shop

📞 New Call Received

Call Summary:
- Caller: John Smith
- Phone: (555) 123-4567
- Duration: 1m 23s
- Status: ✓ completed

⚠️ Special Instructions:
Include order details, pickup time, and customer phone number

AI Summary:
John Smith wants 2 large pepperoni pizzas for pickup at 6:30pm

Full Transcript:
AI: Thank you for calling Aatrox's Pizza. How can I help you today?
Caller: Hi, I'd like to order 2 large pepperoni pizzas for pickup.
AI: Sure! What time would you like to pick them up?
Caller: 6:30pm tonight.
AI: Perfect! Can I get your name and phone number?
Caller: John Smith, 555-123-4567
AI: Got it! We'll have 2 large pepperoni pizzas ready for pickup at 6:30pm. Someone will call you back to confirm. Thank you!

[View in Dashboard Button]
```

**Now business owners never miss a call! 🎉**
