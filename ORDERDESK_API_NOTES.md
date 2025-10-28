# OrderDesk API Documentation - Key Findings

**Source:** https://apidocs.orderdesk.com/
**Date:** October 28, 2025

---

## Overview

OrderDesk provides a RESTful API that accepts and returns JSON. The API allows programmatic access to store data including order status, adding orders, adding shipments, and retrieving inventory items.

---

## Authentication

**Headers Required for Every Request:**

| Header Name | Value |
|-------------|-------|
| ORDERDESK-STORE-ID | Your store ID |
| ORDERDESK-API-KEY | Your API key |
| Content-Type | application/json |

**Fifth Element Credentials:**
- **Store ID:** 125137
- **API Key:** pXmXDSnjdoRsjPYWD6uU2CBCcKPgZUur7SDDSMUa6NR2R4v6mQ

**Location:** Store Settings → API tab

---

## Rate Limits

**Algorithm:** Leaky bucket

**Limits:**
- Initial bucket size: 20 requests
- Refill rate: 3 requests per second
- Results in ~100 requests available over rolling 30 second window

**Monitoring:**
- Check `X-Tokens-Remaining` response header
- If rate limit exceeded, returns 429 status
- `X-Retry-After` header indicates seconds to wait

**Best Practice:** Connect to API in background process, not customer-facing interface. Use asynchronous/cron job approach.

---

## API Usage Best Practices

**Important Guidelines:**
1. **Never assume 100% uptime** - API access should not be assumed
2. **Background processing** - Don't use API in customer-facing order flow
3. **Asynchronous imports** - Use cron jobs to import orders
4. **Valid HTTP/1.* specification** - Follow HTTP RFC 7231

**Common Invalid Requests to Avoid:**
- Sending Content-Length or Content-Type headers during GET requests
- Submitting body during GET request
- Unsupported HTTP methods (CONNECT, TRACE, PATCH)
- Invalid Host headers

---

## Testing Endpoint

**Endpoint:** GET /api/v2/test
**URL:** https://app.orderdesk.me/api/v2/test

**Purpose:** Verify connection is successful and return system time

**Response:**
```json
{
  "status": "success",
  "message": "Connection Successful",
  "current_date_time": "2015-04-14 22:00:10"
}
```

---

## Order Properties

Orders are returned as JSON collections with the following structure:

### Core Order Fields:
- **id** - OrderDesk internal ID (read-only)
- **source_id** - Your order ID (if blank, uses OrderDesk ID)
- **source_name** - Name of order source (cart/marketplace, defaults to "Order Desk")
- **email** - Customer email
- **shipping_method** - Shipping method name
- **quantity_total** - Total quantity of items
- **weight_total** - Total weight
- **product_total** - Subtotal of products
- **shipping_total** - Shipping cost
- **handling_total** - Handling fee
- **tax_total** - Tax amount
- **discount_total** - Total discounts
- **order_total** - Grand total
- **payment_type** - Payment method (Visa, Mastercard, etc.)
- **payment_status** - Payment status (Approved, etc.)
- **customer_id** - Customer identifier
- **tag_name** - Order tag
- **folder_id** - Folder organization
- **date_added** - Order creation date
- **date_updated** - Last update date

### Nested Objects:

**shipping** (object):
- first_name, last_name, company
- address1, address2, address3, address4
- city, state, postal_code, country, phone

**customer** (object):
- first_name, last_name, company
- address1, address2
- city, state, postal_code, country, phone

**return_address** (object):
- title, name, company
- address1, address2
- city, state, postal_code, country, phone

**checkout_data** (object):
- Custom checkout fields (e.g., "Gift Message")

**order_metadata** (object):
- Additional metadata (e.g., fraud_protection_score)

**discount_list** (array):
- name, code, amount

**order_notes** (array):
- date_added, username, content

**order_items** (array):
- id, name, price, quantity, weight, code
- delivery_type, category_code
- variation_list (object): Size, Color, etc.
- metadata (object): image URLs, etc.

**order_shipments** (array):
- id, order_id, tracking_number
- carrier_code, shipment_method
- weight, cost, status
- tracking_url, date_shipped

---

## Available Endpoints

Based on left navigation menu:

1. **Orders** - Order management
2. **Order Items** - Line item management
3. **Shipments** - Shipment tracking
4. **Batch Shipments** - Bulk shipment operations
5. **Inventory Items** - Inventory management
6. **Move Orders** - Order transfer between folders
7. **Store Settings** - Store configuration

---

## Integration Notes

**Contact:** support@orderdesk.com
**Best Practices:** Click link in documentation for integration best practices

**Workflow for Fifth Element:**
1. Customer completes order on fifthelement.photos
2. Payment processed
3. Order submitted to OrderDesk via API
4. OrderDesk notifies owner of new paid order
5. Owner reviews and approves
6. OrderDesk sends to Lumaprints for fulfillment
7. OrderDesk handles all customer communications (emails, tracking)

---

## Next Steps

- Review detailed order creation endpoint
- Review shipment endpoints
- Review webhook configuration
- Test API connection with test endpoint
- Implement order submission workflow

