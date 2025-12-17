# DeskRinger Landing Page

A professional, mobile-first landing page for DeskRinger - an AI phone receptionist service targeting local businesses.

## Features

- **Modern Dark Theme**: Professional dark color scheme with cyan accents
- **Smooth Animations**: Clean hover effects (lift, scale, glow) throughout the site
- **Mobile-First**: Fully responsive design optimized for mobile devices (60% of traffic)
- **Fast Loading**: Minimal JavaScript, Tailwind CSS via CDN
- **Clear CTAs**: Multiple "Book a Demo" buttons throughout the page
- **SEO-Friendly**: Proper meta tags and semantic HTML

## Sections

1. **Hero**: Eye-catching headline with primary CTA
2. **Problem**: Three key pain points for local businesses
3. **How It Works**: Simple 3-step explanation
4. **Pricing**: Transparent pricing starting at $149/month
5. **Who It's For**: Target business types (salons, dentists, gyms, etc.)
6. **CTA**: Final call-to-action with contact options

## Tech Stack

- HTML5
- Tailwind CSS (via CDN)
- Vanilla JavaScript (minimal)
- Google Fonts (Inter)

## Deployment

### Netlify (Recommended)

1. Create a Netlify account at https://www.netlify.com
2. Drag and drop the `website` folder into Netlify
3. Your site will be live in seconds at a netlify.app URL
4. Add a custom domain in Site Settings > Domain Management

### Manual Deployment

The site consists of static files and can be deployed to any web hosting service:
- GitHub Pages
- Vercel
- AWS S3 + CloudFront
- Traditional web hosting

## Customization

### Before Launch - Update These Placeholders:

1. **Calendly Link** (Line 295 in index.html):
   - Replace `https://calendly.com/yourcompany/demo` with your actual Calendly link

2. **Phone Number** (Line 304 in index.html):
   - Replace `(555) 123-4567` with your real phone number
   - Update `tel:5551234567` with the proper format

3. **Email** (Line 328 in index.html):
   - Replace `hello@deskringer.com` with your real email

4. **Logo** (Line 59 in index.html):
   - Optionally add a logo image to replace the text logo

5. **Google Analytics** (Line 21 in index.html):
   - Add your Google Analytics tracking code

### Optional Enhancements:

- Add actual hero image (replace placeholder at line 80)
- Add testimonials section (after getting first customers)
- Add FAQ section (after talking to 10+ customers)
- Add trust badges (BBB, certifications, etc.)
- Add live chat widget (if needed)

## Testing Checklist

- [ ] Test on mobile devices (iPhone, Android)
- [ ] Test on desktop browsers (Chrome, Safari, Firefox)
- [ ] Verify all CTAs work and link to correct URLs
- [ ] Check load time (<2 seconds)
- [ ] Test mobile menu functionality
- [ ] Verify smooth scrolling works
- [ ] Check responsive design at all breakpoints
- [ ] Test contact links (phone, email)

## Performance

- Target: <2 second load time
- Minimal JavaScript for fast performance
- CDN-hosted Tailwind CSS
- Optimized for Core Web Vitals

## Browser Support

- Chrome (latest)
- Safari (latest)
- Firefox (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## File Structure

```
website/
├── index.html          # Main landing page
├── script.js           # Minimal JavaScript for mobile menu and smooth scrolling
├── README.md           # This file
└── assets/
    └── images/         # Add your images here
```

## Next Steps

1. Update all placeholder content (Calendly, phone, email)
2. Optionally add a logo image
3. Deploy to Netlify
4. Test on multiple devices
5. Add Google Analytics
6. Get feedback from 5 local businesses
7. Iterate based on feedback

## Support

For issues or questions, refer to the PROJECT_BRIEF.md in the parent directory.

---

**Ready to launch!** This is an MVP designed for speed and simplicity. Get it live, test with real customers, and iterate based on feedback.
