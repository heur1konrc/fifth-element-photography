# Lumaprints API Documentation - Key Findings

**Source:** https://api-docs.lumaprints.com/
**Date:** October 28, 2025

---

## Authentication

- **Method:** Basic HTTP Authentication
- **Username:** API Key
- **Password:** API Secret
- **Header Format:** `Authorization: Basic {base64(apikey:secret)}`
- **Sandbox URL:** https://sandbox.lumaprints.com/developer/apiKeys
- **Production URL:** https://dashboard.lumaprints.com/developer/apiKeys

---

## Product Structure from API Docs

### Rolled Canvas
- **subcategoryId:** [101005]
- **Options:**
  - Canvas Border: Image Wrap (default), Mirror Wrap, Solid Color
  - Rolled Canvas Border Size: 19, 20, 21 (various border configurations)

### Stretched Canvas
- **subcategoryIds:** [101001, 101002, 101003]
  - **101001:** 0.75in Stretched Canvas
  - **101002:** 1.25in Stretched Canvas
  - **101003:** 1.50in Stretched Canvas

- **Options:**
  - Canvas Border: Image Wrap (default), Mirror Wrap, Solid Color
  - Canvas Hanging Hardware:
    - 4: Sawtooth Hanger installed (default)
    - 5: Hanging Wire installed
    - 6: Black Backboard backing with sawtooth installed
    - 7: Black Backboard backing with hanging wire installed
    - 8: Hanging Wire provided loose
    - 133: Three-point Security Hardware installed
  - 1.25in Canvas Hanging Hardware: 4 (Sawtooth Hanger - default)
  - Canvas Underlayer:
    - 9: None (default)
    - 10: Foamcore Underlayer

### Framed Canvas
- **subcategoryIds:** [102001, 102002, 102003]
  - **102001:** 0.75in Framed Canvas
  - **102002:** 1.25in Framed Canvas
  - **102003:** 1.50in Framed Canvas

- **Options:**
  - Canvas Border: Image Wrap (default), Mirror Wrap, Solid Color
  - Framed Canvas Hanging Hardware:
    - 16: Hanging Wire installed (default)
    - 17: Black Backboard backing with hanging wire installed
    - 18: Hanging Hardware Provided Loose
    - 134: Three-point Security Hardware installed
  - 1.25in Framed Canvas Hanging Hardware: 28 (Hanging Wire installed - default)
  - 0.75in Frame Style:
    - 12: 0.75in Black Floating Frame (default)
    - 13: 0.75in White Floating Frame
    - 14: 0.75in Silver Floating Frame
    - 15: 0.75in Gold Floating Frame
  - 1.25in Frame Style:
    - 27: 1.25in Black Floating Frame (default)
    - 91: 1.25in Oak Floating Frame
    - 120: 1.25in Walnut Floating Frame
  - Canvas Underlayer: N/A for most framed options

---

## API Endpoints Available

### Order Management
- **GET** Get an order
- **GET** Get multiple orders
- **POST** Submit a new order

### Image Management
- **POST** Check image (verify size/compatibility)

### Product Information
- **GET** Retrieve all categories available
- **GET** Retrieve all subcategories under a category
- **GET** Retrieve all options available for the subcategory

### Store Information
- **GET** Get all stores that are available for API order creation

### Shipment Tracking
- **GET** Get shipments of an order

### Pricing
- **POST** Shipping cost

### Webhooks
- **POST** Subscribe to a new event

---

## Important Notes from Documentation

1. **Product Configuration Table:**
   - "The information in this table may not always be up-to-date"
   - "We recommend always using the API endpoints to check for the latest values and options"
   - "This table should be used as a general guide and for quick reference purposes only"

2. **Default Options:**
   - "If no option is provided, the default product options for that subcategory will be used"

3. **API Status:**
   - Currently in open beta
   - Contact: devs@lumaprints.com for issues/suggestions

---

## Next Steps for Documentation Review

- Continue reviewing Fine Art Paper products
- Review Foam-mounted Fine Art Paper products
- Review Metal products
- Review Peel and Stick products
- Document all subcategory IDs and option IDs
- Review order submission format
- Review shipping cost API details
- Review webhook configuration




### Fine Art Paper
- **subcategoryIds:** [103001, 103002, 103003, 103005, 103006, 103007, 103008, 103009]
  - **103001:** Archival Matte Fine Art Paper
  - **103002:** Hot Press Fine Art Paper
  - **103003:** Cold Press Fine Art Paper
  - **103005:** Semi-Glossy Fine Art Paper
  - **103006:** Metallic Fine Art Paper
  - **103007:** Glossy Fine Art Paper
  - **103008:** Semi-Matte Fine Art Paper
  - **103009:** Somerset Velvet Fine Art Paper

- **Options:**
  - Fine Art Paper Bleed:
    - 36: 0.25in Bleed (0.25in on each side) (default)
    - 37: 0.50in Bleed (0.50in on each side)
    - 38: 1.00in Bleed (1.00in on each side)
    - 39: No Bleed (image goes to edge of paper)

### Framed Fine Art Paper
- **subcategoryIds:** [105001, 105002, 105003, 105005, 105006, 105007]
  - **105001:** 0.875in Black Frame
  - **105002:** 0.875in White Frame
  - **105003:** 0.875in Oak Frame
  - **105005:** 1.25in Black Frame
  - **105006:** 1.25in White Frame
  - **105007:** 1.25in Oak Frame

- **Options:**
  - Mat Size:
    - 64: No Mat (default)
    - 65: 1.0 inch on each side
    - 66: 1.5 inch on each side
    - 67: 2.0 inch on each side
    - 68: 2.5 inch on each side
    - 69: 3.0 inch on each side
    - 70: 3.5 inch on each side
    - 71: 4.0 inch on each side
    - 72: 4.5 inch on each side
    - 73: 5.0 inch on each side
  
  - Mat Color:
    - 96: White (default)
    - 97: White with Black Core
    - 98: Smooth Black
    - 99: Antique White
    - 100: Raven Black Rag
    - 101: Dawn Grey
    - 102: Cream
    - 103: Sand
    - 104: Off White
    - 105: Pearl
    - 106: Silver Florentine
    - 107: French Blue
    - 108: Indigo
    - 109: Sauterne
    - 110: Moss Point Green
  
  - Paper Type:
    - 74: Archival Matte Fine Art Paper (default)
    - 75: Hot Press Fine Art Paper
    - 76: Cold Press Fine Art Paper
    - 77: Metallic Fine Art Paper
    - 78: Semi-Glossy Fine Art Paper
    - 79: Glossy Photo Paper
    - 80: Semi-Matte Photo Paper
    - 82: Somerset Velvet
  
  - Framed Fine Art Paper Hanging Hardware:
    - 83: Hanging Wire installed on frame (default)
    - 93: Sawtooth Hanger installed on frame
    - 135: Wire Buddies Hanger installed on frame
  
  - Framed Fine Art Paper Backing:
    - 94: None (default)
    - 95: Kraft Paper

### Metal
- **subcategoryId:** [106001]
  - **106001:** Metal Print

- **Options:**
  - Metal Surface:
    - 29: Glossy White (default)
    - 30: Glossy Silver
  
  - Metal Hanging Hardware:
    - 31: Inset Frame (default)
    - 32: Metal Easel
    - 33: Small (3/4 inch) Stainless Steel Mounting Posts
    - 34: Large (1 inch) Stainless Steel Mounting Posts
    - 35: None

---

## Product Configuration Summary

**Note:** Peel and Stick was not visible in the scrolled content. The documentation indicates it exists but details were not captured.

**Modified:** Almost 2 years ago (as of documentation review date)




---

## Order Submission API

**Endpoint:** POST /api/v1/orders
**Sandbox URL:** https://us.api-sandbox.lumaprints.com/api/v1/orders

### Required Fields:
- **externalId** (string): External order number (1-191 chars)
- **storeId** (number): Store ID to create order under
- **recipient** (object): Shipping address details
  - firstName, lastName, addressLine1, city, state, zipCode, country, phone
  - Optional: addressLine2, company
- **orderItems** (array): Products being ordered
  - externalItemId (string): Line item ID
  - subcategoryId (number): Product subcategory ID
  - quantity (number): Quantity to order
  - width (number): Print width in inches
  - height (number): Print height in inches
  - file (object): Image URL
    - imageUrl (string): Publicly accessible image URL
    - saveImage (boolean): Optional
  - orderItemOptions (array of numbers): Option IDs (uses defaults if not provided)
  - solidColorHexCode (string): Hex color for solid color wrap (only if option 3 selected)

### Optional Fields:
- **shippingMethod** (enum): default, pickup, ground, ground_economy, 2_day, overnight, usps_ground_advantage, usps_priority_mail, etc.
  - Default: "default" (cheapest)
- **productionTime** (enum): regular, nextday, sameday
  - Default: "regular"
- **specialInstructions** (string): Special order notes (1-1024 chars)
- **printouts** (array of URLs): Up to 3 printout URLs to include in package

### Response:
- **201 Success:** Returns order number
- **400 Bad Request:** Validation errors
- **400 Default billing address not set:** Need to set billing in account
- **406 Not Acceptable:** Data format issues

### Important Notes:
- Orders are queued for processing (not instant)
- May take a couple minutes to appear in account
- Image URLs must be publicly accessible

---

## Shipping Cost API

**Endpoint:** POST /api/v1/pricing/shipping
**Sandbox URL:** https://us.api-sandbox.lumaprints.com/api/v1/pricing/shipping

### Purpose:
Calculates shipping costs for available shipping methods based on order details.

### Required Fields:
- **recipient** (object): Destination address
  - addressLine1, city, state, zipCode, country (required)
  - firstName, lastName, company, addressLine2, phone (optional)
- **orderItems** (array): Products to ship
  - subcategoryId (integer): Product type
  - quantity (integer): Number of items
  - width (integer): Width in inches
  - height (integer): Height in inches
  - orderItemOptions (array of integers): Optional, but required for Framed Fine Art Paper (must include mat size)

### Response:
Returns array of available shipping methods with costs:
- carrier (string): USPS, FedEx/UPS/GLS
- method (string): usps_ground_advantage, usps_priority_mail, ground, 2_day, overnight, etc.
- cost (number): Shipping cost in dollars

### Example Response:
```json
{
  "message": "",
  "shippingMethods": [
    {
      "carrier": "USPS",
      "method": "usps_ground_advantage",
      "cost": 9.35
    },
    {
      "carrier": "FedEx/UPS/GLS",
      "method": "overnight",
      "cost": 32.15
    }
  ]
}
```

### Important Notes:
- **PRO TIP:** Can use same payload as order submission to check shipping
- Returns 406 if no shipping method available (e.g., incorrect address, oversized item)
- Shipping costs vary by destination, product size, and weight

---

## API Credentials (Sandbox)

**API Key:** e909ca3adc5026beb5dc306020ffe3068cf0e5962d31303137373136
**Secret:** 23ab680f283aeabd077e2d31303137373136
**Base URL:** https://us.api-sandbox.lumaprints.com

