# AI Receptionist Business - Website Build Brief

## Project Overview
Building a landing page for an AI phone receptionist service targeting local businesses (salons, dentists, gyms, auto shops, HVAC, small medical practices).

## Business Model
- **Product**: AI-powered phone receptionist that answers calls 24/7
- **Pricing**: $99-$299/month per business (starting at $149/month)
- **Value Prop**: No missed calls, no front-desk interruptions, no payroll, immediate ROI
- **Two Tiers**:
  - Version 1 (Basic): Turn-based IVR, reliable, cheaper (~$0.02-0.03/min cost)
  - Version 2 (Premium): Real-time AI, more natural voice, faster (~$0.03-0.10/min cost)

## Tech Stack (Full System)
- **Website**: HTML/CSS/JS → Netlify (what we're building now)
- **Backend API**: Flask + Python → Render ($7/month)
- **Database**: PostgreSQL → Render ($7/month)
- **Telephony**: Twilio
- **AI**: OpenAI (Responses API for V1, Realtime API for V2)

## Website Requirements

### Purpose
Convert local business owners into demo bookings

### Target Audience
- Age: 35-60
- Tech level: Low to medium
- Main pain: Missing calls = lost revenue
- Decision style: Fast, practical, wants immediate results
- Devices: 60% mobile, 40% desktop

### Key Pages/Sections (Single Page Site)

#### 1. Hero Section
- **Headline**: "Never Miss Another Call"
- **Subheadline**: "Your AI receptionist answers 24/7—so you don't have to."
- **CTA Button**: "Book a Demo" (links to Calendly)
- **Visual**: Clean, professional, trustworthy (avoid "techy" aesthetic)

#### 2. The Problem (3 Bullet Points)
- Missed calls = lost customers
- Staff interrupted during appointments
- After-hours calls go to voicemail

#### 3. How It Works (3 Steps)
1. We set up your AI receptionist in minutes
2. It answers calls, takes messages, books callbacks
3. You get instant notifications

#### 4. Pricing
- **Simple tier display**: Starting at $149/month
- No setup fees
- Cancel anytime
- (Don't overcomplicate with multiple tiers yet)

#### 5. CTA Section
- **Primary**: "Book a Demo" button → Calendly link (placeholder for now)
- **Secondary**: Phone/text number for direct contact
- **Email**: Contact email

### Design Guidelines

#### Style
- Clean, professional, trustworthy
- NOT techy/futuristic (avoid neon, sci-fi themes)
- Think: "reliable local business service" not "cutting-edge AI startup"
- Colors: Blues/greens (trust, calm) or neutral (professional)
- Avoid: Excessive animations, auto-playing videos, popups

#### Copy Tone
- Direct and benefit-focused
- Use "you" language (not "we/our")
- Short sentences
- Avoid jargon: Say "AI receptionist" not "conversational AI agent"
- Focus on outcomes: "Never miss a call" not "Advanced NLP technology"

#### Mobile-First
- 60% of traffic will be mobile
- Large tap targets (buttons)
- Readable fonts (16px minimum)
- Fast loading (optimize images)

### Technical Requirements
- **Framework**: Plain HTML/CSS/JS (no React/Vue needed)
- **Styling**: Tailwind CSS preferred (or clean vanilla CSS)
- **Forms**: Contact form should be simple (or just link to Calendly)
- **Deployment**: Will be hosted on Netlify
- **Domain**: Will add custom domain later
- **Analytics**: Add Google Analytics placeholder

### Assets Needed
- Placeholder for logo
- Stock images or illustrations (professional, diverse business types)
- Icons for features (simple, consistent style)

### Must Include
- Clear pricing ($149/month)
- Book demo CTA (at least twice on page)
- Social proof placeholder (testimonials can be added later)
- Trust signals: "No setup fees", "Cancel anytime", "Setup in minutes"

### Must NOT Include (Yet)
- Customer login
- Multiple detailed pricing tiers
- Blog
- FAQ (add after talking to 10 customers)
- About page
- Case studies (don't have them yet)

## File Structure
```
website/
├── index.html
├── styles.css (or use Tailwind CDN)
├── script.js (minimal - smooth scrolling, mobile menu if needed)
├── assets/
│   └── images/
└── README.md
```

## Success Criteria
- Loads in <2 seconds
- Clear value prop in 5 seconds of landing
- Works perfectly on mobile
- One clear action: Book demo
- Professional enough to send to real businesses

## Example Businesses (For Context)
- Amy's Salon (salon owner, 2 staff, misses calls during cuts)
- Dr. Martinez (dentist, front desk overwhelmed, after-hours issues)
- FitCore Gym (owner wants to focus on training, not answering "what are your hours?")

## Placeholder Content
- Calendly link: https://calendly.com/yourcompany/demo (we'll replace)
- Phone: (555) 123-4567
- Email: hello@yourcompany.com
- Business name: [TO BE PROVIDED]

## Developer Notes
- Keep it simple - this is an MVP
- Speed matters more than fancy features
- Real customers will tell us what to add
- We'll iterate based on feedback from first 5 demos

## Next Steps After Website
1. Deploy to Netlify
2. Add custom domain
3. Test on mobile devices
4. Send to 5 local businesses for feedback
5. Book first demo

---

## What We're Building RIGHT NOW
Just the landing page (index.html + styles). The Flask backend, database, and Twilio integration are separate (already planned, not part of this build).
