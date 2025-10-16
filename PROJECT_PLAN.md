# Fifth Element Photography - Mobile Layout Development Plan

## Current Status
- **Desktop Site**: EXCELLENT - Layout, look, and UI are superb. DO NOT TOUCH.
- **Main Branch**: Working perfectly with full desktop and admin functionality
- **Staging Branch**: Needs to be synced to match Main exactly

## Mobile Layout Requirements
Based on screen recording analysis and user specifications:

### Mobile Layout Structure (Completely New - NOT based on desktop)
1. **Header Section**
   - Fifth Element Photography logo and branding
   - Clean, professional presentation

2. **Navigation**
   - "MENU" button that expands to show:
     - Home
     - Featured Image  
     - About
     - Contact
   - Same menu items as desktop (NOT the previous mobile menu structure)

3. **Social Media Section**
   - "Follow Us" heading
   - Facebook and Twitter/X icons

4. **Hero Image Section**
   - Uses SAME image set in Admin (same as desktop)
   - Large, prominent display

5. **Featured Image Section**
   - Has its own dedicated page
   - Same CONTENT as desktop (set in Admin)
   - "FEATURED IMAGE OF THE WEEK" heading
   - Large featured image display
   - "The Story Behind this Image" section
   - Detailed descriptive content
   - Action buttons:
     - "VIEW HIGH RESOLUTION"
     - "DOWNLOAD FULL SIZE" 
     - "SHARE ON SOCIAL MEDIA"

6. **About Page**
   - Same CONTENT as desktop (set in Admin)
   - Mobile-optimized layout

7. **Design Specifications**
   - Vertical scrolling layout
   - Single column, mobile-first design
   - Dark theme (black background)
   - Blue accent colors (#6799c2 style)
   - Clean, modern aesthetic

## Development Approach

### Phase 1: Layout Creation (Static)
- Create completely new mobile template files
- Build static HTML/CSS layout with placeholder content
- NO connection to admin functions initially
- Focus purely on visual layout and structure
- Test layout thoroughly before adding functionality

### Phase 2: Admin Integration (After layout is perfect)
- Connect hero image to admin settings
- Connect featured image content to admin
- Connect about content to admin
- Add proper navigation functionality

## Critical Constraints
- **9K credits remaining** - Must be extremely careful with deployments
- **Work in Staging first** - No direct changes to Main
- **Desktop untouched** - Zero impact on existing desktop functionality
- **Clean slate approach** - No remnants of previous mobile implementation

## File Structure Plan
```
templates/
├── mobile_new.html          # Brand new mobile template
├── mobile_featured.html     # Mobile featured image page
├── mobile_about.html        # Mobile about page
└── (desktop templates unchanged)

static/
├── css/
│   └── mobile_new.css       # Brand new mobile CSS
├── js/
│   └── mobile_new.js        # Brand new mobile JS (if needed)
└── (desktop assets unchanged)
```

## Next Steps
1. ✅ Update this documentation
2. ⏳ Sync Staging to match Main exactly
3. ⏳ Decide whether to continue in current task or start fresh
4. ⏳ Create static mobile layout in Staging
5. ⏳ Test and refine layout
6. ⏳ Add admin integration
7. ⏳ Deploy to Main when perfect

## Repository Information
- **GitHub**: heur1konrc/fifth-element-photography
- **Main Branch**: Production (DO NOT TOUCH directly)
- **Staging Branch**: Development environment
- **Railway URL**: https://fifthelement.photos

## Lessons Learned
- NEVER work directly on Main branch
- Always use proper development workflow
- Test thoroughly in Staging before Main deployment
- Keep desktop and mobile completely separate
- Document everything for continuity
