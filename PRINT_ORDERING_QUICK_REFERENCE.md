# Print Ordering System - Quick Reference

**Status:** Planning Complete
**Date:** October 28, 2025

---

## Key Decisions Made

### Products Offered
✓ Canvas (all 3 wrap depths: 0.75", 1.25", 1.50")  
✓ Framed Canvas (all 3 wrap depths, 1 frame size, 3 colors)  
✓ Fine Art Paper (3 types: Hot Press, Cold Press, Semi-Glossy)  
✓ Foam-mounted Fine Art Paper (same 3 types, most affordable)

### Simplified Options
✓ Canvas Border: Mirror Wrap ONLY  
✓ Hanging Hardware: Hanging Wire ONLY  
✓ Frame Colors: Black, White, Oak ONLY  
✓ Foam Bleed: 0.25" or No Bleed (customer choice)

### Pricing Strategy
✓ Lumaprints prices are wholesale cost  
✓ Admin can adjust markup globally or individually  
✓ Customer sees final retail price only  
✓ Coupon code system for promotions  
✓ Free shipping (likely approach)

### Order Flow
1. Customer orders on fifthelement.photos
2. Payment processed (PayPal likely)
3. Order sent to OrderDesk via API
4. Owner reviews and approves in OrderDesk
5. OrderDesk sends to Lumaprints
6. OrderDesk handles customer emails

### Customer Data Collection
✓ Name, email, address, birthdate (for marketing)  
✗ NO credit card storage (payment processor only)

### Aspect Ratio System
✓ Automatic detection of image aspect ratio  
✓ Show only compatible print sizes  
✓ ~12 sizes per aspect ratio  
✓ Primary ratios: 3:2 and 1:1

---

## API Credentials

### Lumaprints (Sandbox)
- **API Key:** e909ca3adc5026beb5dc306020ffe3068cf0e5962d31303137373136
- **Secret:** 23ab680f283aeabd077e2d31303137373136
- **URL:** https://us.api-sandbox.lumaprints.com

### OrderDesk
- **Store ID:** 125137
- **API Key:** pXmXDSnjdoRsjPYWD6uU2CBCcKPgZUur7SDDSMUa6NR2R4v6mQ
- **URL:** https://app.orderdesk.me/api/v2

---

## Product IDs Reference

### Canvas
- 101001: 0.75" Stretched Canvas
- 101002: 1.25" Stretched Canvas
- 101003: 1.50" Stretched Canvas

### Framed Canvas
- 102001: 0.75" Framed Canvas
- 102002: 1.25" Framed Canvas
- 102003: 1.50" Framed Canvas

### Fine Art Paper
- 103002: Hot Press (smooth)
- 103003: Cold Press (textured)
- 103005: Semi-Glossy (vibrant)

### Options
- Option 2: Mirror Wrap
- Option 5: Hanging Wire installed
- Option 36: 0.25" Bleed
- Option 39: No Bleed

---

## Development Timeline

**Phase 1-2:** Foundation & Product Catalog (Weeks 1-4)  
**Phase 3:** Customer Interface (Weeks 5-7)  
**Phase 4:** Checkout & Payment (Weeks 8-9)  
**Phase 5:** Integration & Testing (Weeks 10-11)  
**Phase 6:** Admin Tools (Week 12)  
**Phase 7:** Beta Launch (Week 13)  
**Phase 8:** Mobile Optimization (Weeks 14-15)  
**Phase 9:** Full Release (Week 16)

---

## Important Notes

1. **White Label:** Customer never sees "Lumaprints" name
2. **Manual Approval:** Owner reviews every order before production
3. **Beta Versioning:** Print ordering has separate beta version number
4. **Pricing Source:** Screenshot Lumaprints pricing page for import
5. **Image URLs:** Must be publicly accessible for Lumaprints API
6. **No Solid Colors:** Not offering solid color canvas borders
7. **Size Limits:** 0.75" canvas max 30x30 (structural limit)
8. **Smallest Size:** Fine Art Paper can go as small as 4x6

---

## Questions Still TBD

- [ ] Final decision on free shipping vs calculated shipping
- [ ] PayPal vs Stripe payment processor
- [ ] Specific sizes for each aspect ratio
- [ ] Exact markup percentages per product
- [ ] Mobile interface design approach
- [ ] Customer account feature set

---

## Documentation Files

1. **PRINT_ORDERING_SYSTEM_PLAN.md** - Complete comprehensive plan
2. **LUMAPRINTS_API_NOTES.md** - Lumaprints API details
3. **ORDERDESK_API_NOTES.md** - OrderDesk API details
4. **PRINT_ORDERING_QUICK_REFERENCE.md** - This file

---

**All documentation committed to Git and pushed to GitHub.**
**Ready to begin development when approved!**

