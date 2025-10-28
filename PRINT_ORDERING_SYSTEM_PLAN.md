# Fifth Element Photography - Print Ordering System Plan

**Version:** Beta 0.1.0
**Date:** October 28, 2025
**Status:** Planning Phase

---

## Executive Summary

This document outlines the complete plan for implementing a print ordering system for Fifth Element Photography. The system will integrate with Lumaprints (print fulfillment) and OrderDesk (order management) to provide customers with a curated selection of high-quality photographic prints while maintaining profitability and operational efficiency.

---

## 1. Business Requirements

### 1.1 Supplier Strategy

**Print Fulfillment Provider:** Lumaprints
- **Rationale:** Affordable for startup, maximizes profit margins
- **Integration:** API-based (Sandbox for development, Production when ready)
- **White Label:** Customer never sees "Lumaprints" branding

**Order Management:** OrderDesk
- **Purpose:** Middleware between Fifth Element and Lumaprints
- **Benefits:** Order review/approval workflow, customer communication handling
- **Integration:** API-based

### 1.2 Product Strategy

**Curated Selection:** Limited, high-quality product offering (NOT full Lumaprints catalog)

**Target Products:**
1. Canvas prints (all wrap depths)
2. Framed Canvas (simplified frame options)
3. Fine Art Paper (3 paper types only)
4. Foam-mounted Fine Art Paper (most affordable option, 3 paper types)

**Simplified Options:**
- Standardized choices to reduce complexity
- Default options where possible
- No solid color borders (Mirror Wrap only)

---

## 2. Product Catalog

### 2.1 Canvas

**Category:** Canvas
**Sub-categories Offered:**
- 0.75" Stretched Canvas (subcategoryId: 101001)
- 1.25" Stretched Canvas (subcategoryId: 101002)
- 1.50" Stretched Canvas (subcategoryId: 101003)

**Options:**
- **Canvas Border:** Mirror Wrap ONLY (no customer choice)
- **Hanging Hardware:** Hanging Wire installed ONLY (no customer choice)

**Sizes:** TBD based on aspect ratio (approximately 12 sizes per ratio)

---

### 2.2 Framed Canvas

**Category:** Framed Canvas
**Sub-categories Offered:**
- 0.75" Framed Canvas (subcategoryId: 102001)
- 1.25" Framed Canvas (subcategoryId: 102002)
- 1.50" Framed Canvas (subcategoryId: 102003)

**Options:**
- **Canvas Border:** Mirror Wrap ONLY
- **Hanging Hardware:** Hanging Wire installed ONLY
- **Frame Size:** 0.875x0.875 ONLY
- **Frame Colors:** 3 choices
  - Black
  - White
  - Oak

**Sizes:** TBD based on aspect ratio

---

### 2.3 Fine Art Paper

**Category:** Fine Art Paper
**Sub-categories Offered (3 types):**
- Hot Press Fine Art Paper (subcategoryId: 103002) - Smooth finish
- Cold Press Fine Art Paper (subcategoryId: 103003) - Textured finish
- Semi-Glossy Fine Art Paper (subcategoryId: 103005) - Vibrant finish

**Options:**
- **Bleed:** 0.25" Bleed (default) or No Bleed

**Sizes:** Can go as small as 4x6 (smaller than other products)

---

### 2.4 Foam-mounted Fine Art Paper

**Category:** Foam-mounted Print
**Sub-categories Offered (3 types):**
- Foam-mounted Hot Press (smooth)
- Foam-mounted Cold Press (textured)
- Foam-mounted Semi-Glossy (vibrant)

**Options:**
- **Bleed Size:** Customer choice
  - 0.25" Bleed (for later framing - adds white border)
  - No Bleed (edge-to-edge, not for framing)

**Sizes:** Can go as small as 4x6

**Note:** Most affordable print option besides bare paper

---

## 3. Size Management Strategy

### 3.1 Aspect Ratio Detection

**Automatic Detection:**
- System detects aspect ratio of full-sized hi-res image
- Matches to predetermined size list for that ratio
- Displays only compatible sizes to customer

**Primary Aspect Ratios:**
- **3:2** (most common - standard digital/35mm film)
  - Landscape: 3:2 (6x4, 9x6, 12x8, 18x12, etc.)
  - Portrait: 2:3 (4x6, 6x9, 8x12, 12x18, etc.)
- **1:1** (square - Instagram style)
  - 8x8, 12x12, 16x16, 20x20, 24x24, etc.

**Additional Ratios:** 4:3, 5:4, 16:9, etc. (as needed)

### 3.2 Size List Management

**Approach:**
- Approximately 12 sizes per aspect ratio
- One size list per aspect ratio
- Universal across all product categories
- Exception: Fine Art Paper and Foam-mounted can go smaller (4x6 minimum)

**Admin Capabilities:**
- Add/remove individual sizes manually
- Import size lists from spreadsheet (bulk)
- Enable/disable specific sizes per ratio
- Set maximum size limits per product type (e.g., 0.75" canvas max 30x30)

### 3.3 Size Limitations

**Structural Constraints:**
- Each product/sub-category has maximum size limits
- Example: 0.75" Canvas cannot support sizes above 30x30 (not strong enough)
- System must enforce these limits

**Aspect Ratio Constraints:**
- Images can ONLY be printed on matching aspect ratios
- 3:2 image → 3:2 print sizes only
- No cropping or aspect ratio conversion offered

---

## 4. Pricing Strategy

### 4.1 Cost Structure

**Lumaprints Pricing:**
- All prices from Lumaprints are WHOLESALE COST
- No pricing API available from Lumaprints
- Pricing varies by:
  - Product category
  - Sub-category
  - Size
  - Options selected

**Pricing Complexity:**
- Every size of every product has unique price
- Every option on every size has unique price
- Example: 0.875x0.875 Black Frame on 8x10 ≠ same frame on 12x14

### 4.2 Pricing Data Sources

**Base Size Pricing:**
- **Source:** Lumaprints pricing page (https://www.lumaprints.com/pricing/)
- **Method:** Screenshot → Manual extraction → Database import
- **Scope:** Limited to ~12 sizes per aspect ratio per product

**Option Pricing:**
- **Source:** Manual entry (not on pricing page)
- **Examples:** Hanging wire cost, frame color upgrades, bleed options
- **Method:** Owner provides prices for database entry

### 4.3 Markup Management

**Admin Requirements:**

**Individual Pricing Control:**
- Adjust price for specific Category/Sub-category/Size combination
- Adjust price for specific Option
- Override any single price point

**Global Pricing Control:**
- Apply markup to ALL products (e.g., +40% across board)
- Apply markup to entire Category (e.g., all Canvas +35%)
- Apply markup to specific Sub-category (e.g., all 1.25" Canvas +30%)
- Bulk price updates

**Customer-Facing Pricing:**
- Show FINAL RETAIL PRICE ONLY (with markup included)
- NEVER show wholesale cost
- NEVER mention "Lumaprints"
- All branding is "Fifth Element Photography"

### 4.4 Coupon Code System

**Admin Capabilities:**
- Create coupon codes (e.g., "SAVENOW", "SUMMER20")
- Set discount type:
  - Percentage off (e.g., 15% off)
  - Dollar amount off (e.g., $10 off)
- Set scope:
  - All products
  - Specific category (e.g., Canvas only)
  - Specific product (e.g., 12x18 Metal only)
- Set expiration date
- Enable/disable coupons
- Track usage

**Customer Experience:**
- Enter coupon code at checkout
- See discount applied to total
- Final price reflects discount

---

## 5. Customer Experience Flow

### 5.1 Order Workflow

**Step-by-Step Process:**

1. **Browse Gallery**
   - Customer views images on fifthelement.photos
   - Gallery organized by categories (Wildlife, Architecture, etc.)

2. **Select Image**
   - Click image to view full size
   - Modal window opens showing image
   - "Order Print" button visible

3. **Order Print (Sidebar Panel)**
   - Sidebar slides in from right (desktop)
   - Image modal remains visible on left
   - Order interface appears in sidebar

4. **Select Product (Category)**
   - Choose: Canvas, Framed Canvas, Fine Art Paper, or Foam-mounted
   - Visual representation of each product type

5. **Select Sub-category**
   - Based on category chosen
   - Example: Canvas → Choose 0.75", 1.25", or 1.50" wrap depth
   - Example: Fine Art Paper → Choose Hot Press, Cold Press, or Semi-Glossy

6. **Select Size**
   - System detects image aspect ratio
   - Displays only compatible sizes
   - Shows price for each size
   - Prices include markup (retail price)

7. **Select Options (if applicable)**
   - Most options are default/automatic
   - Customer choices limited to:
     - Framed Canvas: Frame color (Black, White, Oak)
     - Foam-mounted: Bleed size (0.25" or No Bleed)

8. **See Final Price**
   - Price updates in real-time
   - Includes all selections
   - Retail price (with markup)

9. **Add to Cart or Checkout**
   - **Add to Cart:** Return to gallery, repeat process for more images
   - **Checkout:** Proceed to payment

### 5.2 Shopping Cart

**Functionality:**
- Multiple items can be added
- Each image can be ordered in different sizes/products
- Cart persists while shopping
- View cart contents before checkout
- Edit quantities or remove items

**Rationale:** Different images have different aspect ratios, so one-at-a-time selection makes sense

### 5.3 Checkout Process

**Required Information:**
- Account creation/login
- Shipping address
- Payment information (NOT stored)

**Shipping Strategy:**
- **Likely:** Free shipping (simplifies everything)
- **Alternative:** Calculated shipping via Lumaprints API
- **Decision:** TBD after reviewing shipping costs

**Payment Processing:**
- **Likely:** PayPal (lower fees)
- **Alternative:** Stripe (better UX, higher fees)
- **Decision:** TBD
- **System Design:** Payment-processor agnostic (easy to swap)

---

## 6. Customer Account System

### 6.1 Account Requirements

**Must Collect:**
- Full name
- Email address
- Shipping address
- Birthdate

**Must NOT Store:**
- Credit card information (handled by payment processor only)
- Payment details

**Purpose:**
- Marketing campaigns
- Birthday promotions
- Email newsletters
- Customer segmentation

### 6.2 Account Capabilities (TBD)

**Potential Features:**
- Order history viewing
- Saved addresses
- Favorite images
- Reorder previous prints
- Profile management

**Initial MVP:**
- Account creation with data collection
- Basic login/logout
- Add features later as needed

---

## 7. Order Management Workflow

### 7.1 Order Flow

**Three-Stage Process:**

**Stage 1: Fifth Element → OrderDesk**
- Customer completes order on fifthelement.photos
- Payment processed (PayPal or Stripe)
- Order automatically submitted to OrderDesk via API

**Stage 2: OrderDesk → Owner Notification**
- OrderDesk notifies owner of new paid order
- Order status: "Awaiting deployment"
- Owner reviews order details in OrderDesk dashboard

**Stage 3: Owner → Lumaprints Approval**
- Owner checks order for accuracy
- Owner approves and sends to Lumaprints
- OrderDesk handles Lumaprints submission

### 7.2 Order Communication

**Customer Communications (OrderDesk Handles):**
- Order confirmation emails
- Order status updates
- Shipping notifications
- Tracking information
- Delivery confirmations

**Customer Support:**
- Email: support@fifthelement.photos (goes to owner)
- OrderDesk can handle customer inquiries

**Fifth Element System:**
- Collects order
- Processes payment
- Submits to OrderDesk
- NO email sending required (OrderDesk handles it)

### 7.3 Admin Order Management

**Phase 1 (Minimal):**
- View orders on Lumaprints dashboard
- View orders on OrderDesk dashboard
- Tracking, progress, MFR dates, ship dates available there
- NO order viewing in Fifth Element admin (skip for now)

**Phase 2 (Future):**
- Consolidated order view in Fifth Element admin
- Nice-to-have feature for later

**Refund Handling:**
- Refund requests via form (not admin interface)

---

## 8. Technical Integration

### 8.1 Lumaprints API Integration

**API Credentials (Sandbox):**
- API Key: e909ca3adc5026beb5dc306020ffe3068cf0e5962d31303137373136
- Secret: 23ab680f283aeabd077e2d31303137373136
- Base URL: https://us.api-sandbox.lumaprints.com

**Authentication:**
- Method: Basic HTTP Authentication
- Header: `Authorization: Basic {base64(apikey:secret)}`

**Key Endpoints:**

1. **GET /api/v1/products/categories**
   - Retrieve all available categories

2. **GET /api/v1/products/categories/{categoryId}/subcategories**
   - Retrieve subcategories for a category

3. **GET /api/v1/products/subcategories/{subcategoryId}/options**
   - Retrieve options for a subcategory

4. **POST /api/v1/orders**
   - Submit new order for fulfillment

5. **POST /api/v1/images/check**
   - Verify image size/compatibility

6. **POST /api/v1/pricing/shipping**
   - Calculate shipping costs

7. **GET /api/v1/orders/{orderId}/shipments**
   - Get shipment tracking info

**Order Submission Format:**
```json
{
  "externalId": "FE-ORDER-12345",
  "storeId": 818,
  "shippingMethod": "default",
  "productionTime": "regular",
  "recipient": {
    "firstName": "John",
    "lastName": "Smith",
    "addressLine1": "123 Main St",
    "city": "Nashville",
    "state": "TN",
    "zipCode": "37201",
    "country": "US",
    "phone": "615-555-1234"
  },
  "orderItems": [{
    "externalItemId": "ITEM-1",
    "subcategoryId": 101002,
    "quantity": 1,
    "width": 12,
    "height": 18,
    "file": {
      "imageUrl": "https://fifthelement.photos/images/original/image123.jpg"
    },
    "orderItemOptions": [2, 5]
  }]
}
```

### 8.2 OrderDesk API Integration

**API Credentials:**
- Store ID: 125137
- API Key: pXmXDSnjdoRsjPYWD6uU2CBCcKPgZUur7SDDSMUa6NR2R4v6mQ
- Base URL: https://app.orderdesk.me/api/v2

**Authentication:**
- Headers Required:
  - `ORDERDESK-STORE-ID: 125137`
  - `ORDERDESK-API-KEY: pXmXDSnjdoRsjPYWD6uU2CBCcKPgZUur7SDDSMUa6NR2R4v6mQ`
  - `Content-Type: application/json`

**Rate Limits:**
- 20 requests initial bucket
- 3 requests/second refill rate
- ~100 requests per 30-second window
- Monitor `X-Tokens-Remaining` header

**Key Endpoints:**

1. **GET /api/v2/test**
   - Test connection

2. **POST /api/v2/orders**
   - Submit new order to OrderDesk

3. **GET /api/v2/orders/{orderId}**
   - Get order details

4. **GET /api/v2/shipments**
   - Get shipment information

**Best Practices:**
- Use background/async processing (not customer-facing)
- Implement cron job for order submission
- Never assume 100% API uptime
- Follow HTTP/1.* specification

### 8.3 Image Management

**Image Storage:**
- Original hi-res images stored in persistent volume
- Path: /mnt/fifth-element-images/original/
- Publicly accessible URLs for Lumaprints API

**Image URL Format:**
- Example: https://fifthelement.photos/images/original/wildlife_eagle_001.jpg
- Must be publicly accessible (Lumaprints fetches from URL)

**Image Analysis:**
- Detect aspect ratio automatically
- Calculate dimensions
- Verify print suitability (existing "Analyze" feature)
- Show compatible print sizes

---

## 9. User Interface Design

### 9.1 Desktop Experience

**Gallery View:**
- Grid layout of images
- Category filtering
- Image hover effects
- Click to view/order

**Image Modal:**
- Full-size image display
- Image details (title, category, description)
- "Order Print" button prominent

**Order Sidebar (Slides from Right):**
- Product selection interface
- Step-by-step progression
- Real-time price updates
- Visual product representations
- Add to cart or checkout buttons

**Shopping Cart:**
- Cart icon with item count
- Cart dropdown or page
- Edit quantities, remove items
- Proceed to checkout

**Checkout Page:**
- Account login/creation
- Shipping address form
- Payment processing
- Order review
- Submit order

### 9.2 Mobile Experience

**Design Later:**
- Desktop-first approach
- Optimize mobile after desktop works
- Likely approach:
  - Full-screen product selection
  - Bottom sheet interface
  - Touch-optimized controls

### 9.3 Admin Interface

**Pricing Management:**
- View all products and prices
- Edit individual prices
- Apply global markup
- Apply category/subcategory markup
- Import prices from spreadsheet
- Export prices to spreadsheet

**Product Management:**
- Enable/disable categories
- Enable/disable sub-categories
- Enable/disable specific sizes
- Set size limits per product

**Size List Management:**
- Define aspect ratios
- Assign size lists to ratios
- Add/remove individual sizes
- Import size lists from spreadsheet

**Coupon Management:**
- Create/edit coupons
- Set discount type and amount
- Set scope and expiration
- Enable/disable coupons
- View usage statistics

**Order Management (Phase 2):**
- View orders (future)
- Search/filter orders (future)
- Export orders (future)

---

## 10. Version Management

### 10.1 Version Strategy

**Main Site & Admin:**
- Current: v2.0.0 (production)
- Updates as core functionality changes
- Displayed in admin dashboard only

**Print Ordering System:**
- Separate Beta versioning
- Example: "Print Ordering: Beta v0.5.0"
- Remains in beta until fully tested and released
- Beta status indicates non-essential for core site

**Version Display:**
- Admin dashboard shows both versions:
  - Admin Version: v2.0.0
  - Website Version: v2.0.0
  - Print Ordering: Beta v0.1.0 (when implemented)

### 10.2 Version Updates

**Automatic Updates:**
- Version numbers update as changes are made
- Documented in version logs
- Git commits tagged with versions

**Beta Progression:**
- Beta v0.1.0 → Initial development
- Beta v0.5.0 → Feature complete, testing
- Beta v0.9.0 → Pre-release candidate
- v1.0.0 → Official release (no longer beta)

---

## 11. Development Phases

### Phase 1: Foundation (Weeks 1-2)
- Set up database schema for products, pricing, sizes
- Implement Lumaprints API authentication
- Implement OrderDesk API authentication
- Test API connections
- Create product data models

### Phase 2: Product Catalog (Weeks 3-4)
- Import product categories and subcategories from Lumaprints API
- Build admin interface for product management
- Implement size list management
- Import pricing data from screenshots
- Build pricing management interface

### Phase 3: Customer Interface (Weeks 5-7)
- Build image selection modal
- Build order sidebar interface
- Implement product selection flow
- Implement size selection with aspect ratio detection
- Implement real-time price calculation
- Build shopping cart

### Phase 4: Checkout & Payment (Weeks 8-9)
- Build customer account system
- Implement account creation/login
- Build checkout interface
- Integrate payment processor (PayPal or Stripe)
- Implement order submission to OrderDesk

### Phase 5: Integration & Testing (Weeks 10-11)
- Test complete order flow (Sandbox)
- Test payment processing
- Test OrderDesk integration
- Test Lumaprints order submission
- Fix bugs and refine UX

### Phase 6: Admin Tools (Week 12)
- Build coupon management
- Build pricing adjustment tools
- Build product enable/disable controls
- Test admin workflows

### Phase 7: Beta Launch (Week 13)
- Switch to Lumaprints production API
- Soft launch to limited audience
- Monitor orders and customer feedback
- Refine based on real-world usage

### Phase 8: Mobile Optimization (Weeks 14-15)
- Design mobile interface
- Implement responsive ordering flow
- Test on various devices
- Optimize performance

### Phase 9: Full Release (Week 16)
- Public announcement
- Remove beta label
- Version 1.0.0 release
- Marketing push

---

## 12. Success Metrics

### 12.1 Business Metrics
- Order conversion rate (gallery views → orders)
- Average order value
- Profit margin per order
- Customer acquisition cost
- Customer lifetime value
- Repeat customer rate

### 12.2 Technical Metrics
- API uptime and reliability
- Order processing time
- Page load times
- Mobile vs desktop usage
- Cart abandonment rate
- Payment success rate

### 12.3 Customer Satisfaction
- Order accuracy rate
- Shipping time satisfaction
- Product quality feedback
- Customer support inquiries
- Refund/return rate
- Net Promoter Score

---

## 13. Risk Management

### 13.1 Technical Risks

**API Dependency:**
- Risk: Lumaprints or OrderDesk API downtime
- Mitigation: Queue orders locally, retry mechanism, customer notification

**Payment Processing:**
- Risk: Payment processor issues
- Mitigation: Secondary payment option, clear error messages

**Image Quality:**
- Risk: Customer orders print too large for image resolution
- Mitigation: Image analysis tool, size recommendations, warnings

### 13.2 Business Risks

**Pricing Errors:**
- Risk: Incorrect pricing leads to losses
- Mitigation: Thorough testing, admin review before launch, price alerts

**Order Fulfillment:**
- Risk: Lumaprints quality issues or delays
- Mitigation: Order review workflow, quality checks, customer communication

**Customer Expectations:**
- Risk: Product doesn't match customer expectations
- Mitigation: Clear product descriptions, sample images, return policy

### 13.3 Operational Risks

**Manual Approval Bottleneck:**
- Risk: Owner unavailable to approve orders
- Mitigation: Mobile access to OrderDesk, backup approval process

**Customer Support Load:**
- Risk: Too many support inquiries
- Mitigation: Comprehensive FAQ, OrderDesk handles routine emails

**Pricing Maintenance:**
- Risk: Lumaprints changes prices, our prices become outdated
- Mitigation: Regular price audits, admin alerts for price changes

---

## 14. Future Enhancements

### 14.1 Short-term (6 months)
- Add more product types (Metal prints, Peel & Stick)
- Expand size offerings
- Implement customer reviews
- Add gift certificates
- Bulk order discounts

### 14.2 Mid-term (12 months)
- Custom framing options
- Image editing tools (crop, adjust)
- Subscription service (monthly print)
- Corporate/wholesale ordering
- Mobile app

### 14.3 Long-term (24 months)
- Print-on-demand merchandise (mugs, t-shirts, etc.)
- Artist collaboration platform
- Print marketplace (sell other photographers' work)
- International shipping
- Gallery partnerships

---

## 15. Documentation & Training

### 15.1 Technical Documentation
- API integration guides
- Database schema documentation
- Code documentation
- Deployment procedures
- Troubleshooting guides

### 15.2 User Documentation
- Customer ordering guide
- FAQ section
- Product descriptions
- Size guide
- Care instructions for prints

### 15.3 Admin Documentation
- Admin interface guide
- Pricing management procedures
- Order approval workflow
- Coupon creation guide
- Product management guide

---

## 16. Conclusion

This comprehensive plan outlines the complete print ordering system for Fifth Element Photography. The system is designed to be:

- **Profitable:** Curated product selection with markup control
- **Scalable:** API-based integrations allow growth
- **User-friendly:** Simplified customer experience
- **Manageable:** Owner approval workflow and admin tools
- **Professional:** White-label branding, quality products

The phased development approach allows for iterative testing and refinement, with a beta launch to validate the system before full release. By leveraging Lumaprints for fulfillment and OrderDesk for order management, Fifth Element Photography can focus on what it does best: creating stunning photography and providing excellent customer service.

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 development
3. Set up development environment
4. Test API connections
5. Start building!

---

**Document Version:** 1.0
**Last Updated:** October 28, 2025
**Author:** Manus AI Assistant
**Approved By:** [Pending Owner Review]

