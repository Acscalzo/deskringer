# DeskRinger Admin Dashboard

Professional admin dashboard for managing DeskRinger customers and call logs.

## Features

- **Authentication** - Secure login with JWT tokens
- **Dashboard** - Real-time stats (customers, calls, metrics)
- **Customer Management** - Add, edit, view customers
- **Call Logs** - View all calls with transcripts
- **Responsive** - Works on desktop and mobile

## Tech Stack

- HTML5
- CSS3 (Custom dark theme)
- Vanilla JavaScript
- Connects to Flask API on Render

## Pages

1. **Login** (`index.html`) - Admin authentication
2. **Dashboard** (`dashboard.html`) - Overview with stats
3. **Customers** (`customers.html`) - Customer CRUD operations
4. **Calls** (`calls.html`) - Call logs and transcripts

## Setup

### API Configuration

The dashboard connects to the backend API at:
```
https://deskringer-api.onrender.com
```

This is configured in `js/config.js`. Update the `API_BASE_URL` if your backend is hosted elsewhere.

### Local Testing

1. Open `index.html` in a browser
2. Login with your admin credentials

**Note:** You may encounter CORS issues when testing locally. Deploy to Netlify for full functionality.

## Deployment to Netlify

### Option 1: Drag & Drop (Easiest)

1. Go to https://app.netlify.com
2. Drag the `admin-site` folder into Netlify
3. Done! Your site is live

### Option 2: GitHub Deploy (Recommended)

1. Push code to GitHub
2. In Netlify, click "New site from Git"
3. Connect to your GitHub repo: `Acscalzo/deskringer`
4. Settings:
   - **Branch:** main
   - **Base directory:** admin-site
   - **Publish directory:** (leave empty or use `.`)
5. Deploy!

### Option 3: Netlify CLI

```bash
cd admin-site
netlify deploy --prod
```

## Custom Domain

Once deployed, set up custom domain:

1. In Netlify dashboard → Domain settings
2. Add custom domain: `admin.deskringer.com`
3. Configure DNS:
   - Add CNAME record: `admin` → your-site.netlify.app
4. Enable HTTPS (automatic via Netlify)

## Environment

The dashboard is configured to connect to production API by default. No environment variables needed!

## Authentication Flow

1. User enters credentials on login page
2. Credentials sent to `/api/admin/login`
3. Backend returns JWT token
4. Token stored in `localStorage`
5. Token sent with all subsequent API requests
6. Token expires after 24 hours

## Security

- ✅ JWT authentication on all requests
- ✅ Token stored in localStorage
- ✅ Auto-logout on token expiration
- ✅ Protected routes (redirect to login if not authenticated)
- ✅ HTTPS enforced by Netlify

## Features Overview

### Dashboard Page
- Total customers (active, trial, cancelled)
- Total calls (all time, today)
- Average call duration
- Recent calls list
- System status

### Customers Page
- List all customers
- Add new customer
- Edit customer details
- View customer status
- Filter by status (coming soon)

### Calls Page
- List all calls
- View call details
- Read transcripts
- See callback requests
- Call statistics

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### "Failed to fetch" errors
- Check that backend API is running
- Verify API URL in `js/config.js`
- Check browser console for CORS errors

### "Token expired" errors
- Login again to get new token
- Token lasts 24 hours

### Can't login
- Verify credentials
- Check backend logs on Render
- Ensure database has admin user

## Next Steps

1. ✅ Deploy to Netlify
2. Set up custom domain `admin.deskringer.com`
3. Test all features
4. Add customers
5. Integrate Twilio for real calls

## Support

Backend API: https://deskringer-api.onrender.com
GitHub: https://github.com/Acscalzo/deskringer
