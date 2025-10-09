#!/usr/bin/env python3
"""
Submit a test order to the Lumaprints API using perfectly resized user photograph.
"""

import json
from lumaprints_api import get_lumaprints_client

def submit_test_order():
    """Submit a test order to the Lumaprints API."""
    print("=== Submitting Test Order to Lumaprints ===")

    # Initialize Lumaprints API client
    api = get_lumaprints_client(sandbox=True)  # Use sandbox

    # Sample order data using perfectly resized user photograph
    order_data = {
        "externalId": "TEST-ORDER-12349",
        "storeId": "20027",
        "shippingMethod": "default",
        "productionTime": "regular",
        "recipient": {
            "firstName": "John",
            "lastName": "Doe",
            "addressLine1": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zipCode": "90210",
            "country": "US"
        },
        "orderItems": [{
            "externalItemId": "TEST-ORDER-12349-1",
            "subcategoryId": 103001,  # Archival Matte Fine Art Paper
            "quantity": 1,
            "width": 8,
            "height": 12,
            "file": {
                "imageUrl": "https://files.manuscdn.com/user_upload_by_module/session_file/310519663082973493/EKlVhkDRzWYURWqV.jpg"
            },
            "orderItemOptions": []
        }]
    }

    try:
        # Submit the order
        response = api.submit_order(order_data)
        print("✅ Order submitted successfully!")
        print(json.dumps(response, indent=2))
        return response
    except Exception as e:
        print(f"❌ Order submission failed: {e}")
        return None

if __name__ == "__main__":
    submit_test_order()
