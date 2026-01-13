# SendGrid Setup Guide - Fix Spam/Junk Mail Issues

## Current Status
✅ SendGrid is configured on Render (production)
❌ Emails going to junk/spam folder

## Why Emails Go to Spam

1. **Unverified sender domain** - Using notifications@deskringer.com without domain authentication
2. **No SPF/DKIM records** - Email providers can't verify emails are legitimate
3. **New sender reputation** - SendGrid account is new, no sending history
4. **Missing sender name** - Was just showing email address (FIXED in code)

## Step-by-Step Fix

### Option A: Use Your Own Domain (RECOMMENDED)

**Best approach:** Use an email address from a domain you own (e.g., notifications@yourdomain.com)

1. **Log into SendGrid** (https://app.sendgrid.com)

2. **Go to Settings → Sender Authentication**
   - Click "Authenticate Your Domain"
   - Choose your DNS host provider
   - Follow instructions to add DNS records (usually CNAME records)
   - This adds SPF/DKIM authentication

3. **Update environment variable on Render:**
   ```
   NOTIFICATION_FROM_EMAIL=noreply@yourdomain.com
   NOTIFICATION_FROM_NAME=DeskRinger
   ```

4. **Wait for DNS propagation** (can take 24-48 hours)

5. **Test email** from Admin Settings page

**Result:** Emails will land in inbox, not spam

---

### Option B: Use SendGrid's Single Sender Verification (Quick Fix)

If you don't have your own domain yet, use a Gmail/Outlook address:

1. **Log into SendGrid**

2. **Go to Settings → Sender Authentication → Single Sender Verification**

3. **Create a verified sender:**
   - From Name: DeskRinger
   - From Email: your-real-email@gmail.com (you must have access to this inbox)
   - Reply To: Same or different email
   - Company: DeskRinger

4. **Check email and click verification link**

5. **Update Render environment variables:**
   ```
   NOTIFICATION_FROM_EMAIL=your-real-email@gmail.com
   NOTIFICATION_FROM_NAME=DeskRinger
   ```

6. **Test email** from Admin Settings

**Result:** Better than before, but Gmail/Outlook addresses still more likely to be flagged

---

### Option C: Use a Free Domain Alternative

If you want a professional email but don't have a domain:

1. **Register free domain** at Freenom.com or get cheap domain ($12/yr) at Namecheap
2. **Set up email forwarding** (Cloudflare Email Routing is free)
3. **Follow Option A steps above**

---

## Additional Improvements (Already Done in Code)

✅ Added sender name "DeskRinger" (instead of just email)
✅ Professional HTML email templates
✅ Clear subject lines
✅ Proper email structure

## Environment Variables Needed on Render

```bash
SENDGRID_API_KEY=your-sendgrid-api-key-here
NOTIFICATION_FROM_EMAIL=notifications@yourdomain.com  # Change to your verified email
NOTIFICATION_FROM_NAME=DeskRinger
```

## Testing

After setup:
1. Go to Admin Dashboard → Settings
2. Enter your email in "Test Email Address"
3. Click "Send Test Email"
4. Check inbox (not spam folder)

## Troubleshooting

### Still going to spam after domain authentication?
- **Wait 48 hours** for DNS propagation
- **Send more emails** - new sender reputation takes time (10-20 emails)
- **Ask recipients to mark as "Not Spam"** - improves reputation
- **Check spam score**: Use https://www.mail-tester.com

### Using Gmail as sender?
- Gmail requires "Allow less secure apps" (not recommended)
- Better to use dedicated sending domain

### Emails not sending at all?
- Check Render logs for errors
- Verify SENDGRID_API_KEY is correct
- Check SendGrid dashboard for error logs

## Current Configuration

Your **production** (Render) should have:
- ✅ SENDGRID_API_KEY set (you mentioned emails are sending)
- ⚠️ NOTIFICATION_FROM_EMAIL needs to be verified domain
- ⚠️ Need to authenticate domain in SendGrid

## Recommendation

**For now (pilot customers):**
- Use Option B (Single Sender Verification with your Gmail/personal email)
- Takes 5 minutes to set up
- Good enough for 5-10 pilot customers

**Before scaling (20+ customers):**
- Use Option A (Authenticate your own domain)
- Professional appearance
- Better deliverability
- Required for high volume

---

**Next Step:** Choose Option A or B above, then update your Render environment variables and test!
