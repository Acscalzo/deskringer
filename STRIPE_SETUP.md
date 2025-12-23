# Stripe Integration Setup Guide

This guide will help you set up Stripe payment processing for DeskRinger.

## Overview

You'll be using **Option 1: Manual Payment Links**, which means:
1. You create customers in admin dashboard
2. You generate payment links via admin dashboard
3. You send payment links to customers (email, text, etc.)
4. Customers pay via Stripe
5. Webhooks automatically update subscription status

---

## Step 1: Create Stripe Account

1. Go to https://stripe.com
2. Click "Start now" or "Sign up"
3. Complete the registration process
4. Verify your email

**Note:** Start in **Test Mode** - you can test everything without real payments.

---

## Step 2: Create a Subscription Product

### In Stripe Dashboard:

1. Go to **Products** (https://dashboard.stripe.com/products)
2. Click **"+ Add product"**
3. Fill in the details:
   - **Name:** DeskRinger AI Receptionist
   - **Description:** AI-powered phone answering service for businesses
   - **Pricing model:** Recurring
   - **Price:** $149.00 USD
   - **Billing period:** Monthly
4. Click **"Save product"**
5. **IMPORTANT:** Copy the **Price ID** (looks like `price_xxxxxxxxxxxxx`)
   - You'll need this for the `STRIPE_PRICE_ID` environment variable

---

## Step 3: Get Your API Keys

### Test Mode (Recommended to Start)

1. Make sure you're in **Test Mode** (toggle in top-right of Stripe dashboard)
2. Go to **Developers** → **API keys** (https://dashboard.stripe.com/test/apikeys)
3. Copy these keys:
   - **Publishable key:** Starts with `pk_test_...` (you don't need this for Option 1)
   - **Secret key:** Starts with `sk_test_...` ⬅️ **YOU NEED THIS**
     - Click "Reveal test key token" and copy it

### Live Mode (When Ready to Accept Real Payments)

1. Toggle to **Live Mode** in top-right
2. Go to **Developers** → **API keys** (https://dashboard.stripe.com/apikeys)
3. Copy the **Secret key** (starts with `sk_live_...`)

---

## Step 4: Set Up Webhook

Stripe uses webhooks to notify your backend when payments happen.

### Create Webhook Endpoint:

1. Go to **Developers** → **Webhooks** (https://dashboard.stripe.com/test/webhooks)
2. Click **"+ Add endpoint"**
3. Enter the following details:
   - **Endpoint URL:** `https://deskringer-api.onrender.com/api/webhooks/stripe/webhook`
   - **Description:** DeskRinger subscription webhooks
   - **Events to send:** Select these events:
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
4. Click **"Add endpoint"**
5. **IMPORTANT:** Copy the **Signing secret** (looks like `whsec_xxxxxxxxxxxxx`)
   - You'll need this for the `STRIPE_WEBHOOK_SECRET` environment variable

---

## Step 5: Add Environment Variables to Render

Now add your Stripe keys to your backend on Render:

1. Go to https://dashboard.render.com
2. Select your **deskringer-api** service
3. Go to **Environment** tab
4. Add these 3 new environment variables:

| Key | Value |
|-----|-------|
| `STRIPE_API_KEY` | Your secret key from Step 3 (`sk_test_...` or `sk_live_...`) |
| `STRIPE_WEBHOOK_SECRET` | Your webhook signing secret from Step 4 (`whsec_...`) |
| `STRIPE_PRICE_ID` | Your price ID from Step 2 (`price_...`) |

5. Click **"Save Changes"**
6. Render will automatically redeploy your backend (takes 2-3 minutes)

---

## Step 6: Test the Integration

### Test in Stripe Test Mode:

1. Log into your admin dashboard: https://deskringer-admin.netlify.app
2. Create a test customer (or use existing one)
3. Click the **"💳 Payment Link"** button
4. You'll see a Stripe payment link (copied to clipboard)
5. Open the link in a new browser window
6. Use Stripe's test card numbers:
   - **Successful payment:** `4242 4242 4242 4242`
   - **Expiry:** Any future date (e.g., 12/25)
   - **CVC:** Any 3 digits (e.g., 123)
   - **ZIP:** Any 5 digits (e.g., 12345)
7. Complete the payment
8. Go back to admin dashboard → Customers
9. The customer's status should update to **"active"** within a few seconds

### Check Webhook Logs:

1. Go to Stripe Dashboard → **Developers** → **Webhooks**
2. Click on your webhook endpoint
3. You should see successful webhook deliveries
4. If you see errors, check Render logs for details

---

## Step 7: Go Live (When Ready)

When you're ready to accept real payments:

1. **Complete Stripe account verification**
   - Provide business details
   - Add bank account for payouts
   - Verify identity (if required)

2. **Switch to Live Mode:**
   - Toggle to **Live Mode** in Stripe dashboard
   - Create the same product in Live Mode
   - Get Live API keys
   - Create Live webhook endpoint

3. **Update Render environment variables:**
   - Change `STRIPE_API_KEY` to your live key (`sk_live_...`)
   - Change `STRIPE_WEBHOOK_SECRET` to your live webhook secret
   - Change `STRIPE_PRICE_ID` to your live price ID

4. **Test with a real card** (use a small amount or cancel immediately)

---

## How to Use (Customer Flow)

### For Each New Customer:

1. **Create customer in admin dashboard:**
   - Business name, email, contact info
   - Configure AI greeting and instructions
   - Assign them a Twilio phone number (or keep trial number for now)

2. **Generate payment link:**
   - Click "💳 Payment Link" button
   - Link is copied to clipboard automatically

3. **Send link to customer:**
   - Email: "Here's your payment link to get started: [link]"
   - Text message with the link
   - However you communicate with them

4. **Customer pays:**
   - They click the link
   - Enter card details
   - Subscribe for $149/month

5. **Automatic activation:**
   - Stripe webhook fires
   - Backend updates customer status to "active"
   - You see it in admin dashboard
   - Customer can start using their AI receptionist!

---

## Troubleshooting

### Payment link doesn't work
- Check that `STRIPE_PRICE_ID` is set correctly in Render
- Make sure you're using the right price ID (test vs live mode)
- Check Render logs for errors

### Webhook not firing
- Verify webhook URL is correct: `https://deskringer-api.onrender.com/api/webhooks/stripe/webhook`
- Check that `STRIPE_WEBHOOK_SECRET` matches your webhook signing secret
- Look at webhook logs in Stripe dashboard for delivery errors

### Subscription status not updating
- Check Render logs for webhook errors
- Verify the customer has a `stripe_customer_id` set (check in database)
- Make sure webhook is sending the right events

### "Stripe price not configured" error
- The `STRIPE_PRICE_ID` environment variable is missing or incorrect
- Go to Render → Environment → Add `STRIPE_PRICE_ID`

---

## Pricing Recommendation

**Basic Tier:** $149/month
- Unlimited calls
- AI receptionist
- Call transcripts
- Email notifications
- Basic support

**Premium Tier:** $299/month (future)
- Everything in Basic
- OpenAI Realtime API (faster, more natural)
- Priority support
- Custom voice training
- CRM integration

---

## Next Steps

1. ✅ Set up Stripe account
2. ✅ Create subscription product
3. ✅ Get API keys
4. ✅ Set up webhook
5. ✅ Add environment variables to Render
6. ✅ Test with test cards
7. ✅ Deploy admin dashboard changes (manual Netlify deploy)
8. 🎯 Get your first customer!

---

## Support

If you run into issues:
- Check Render logs: https://dashboard.render.com
- Check Stripe webhook logs: https://dashboard.stripe.com/test/webhooks
- Verify all environment variables are set correctly

---

**You're now ready to accept payments and get your first customer! 🎉**
