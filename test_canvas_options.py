#!/usr/bin/env python3

import requests
import base64
import json

# Test Lumaprints API for Canvas options
API_KEY = "c5675f9b5bcab0799a49bba00da28405f2ca2ab72d31303137373136"
API_SECRET = "541614636cad6ba7f6be2d31303137373136"

# Create authentication header
credentials = f"{API_KEY}:{API_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

base_url = "https://us.api-sandbox.lumaprints.com/api/v1"

print("Testing Canvas subcategory options...")

try:
    # First get Canvas subcategories
    canvas_url = f"{base_url}/products/categories/101/subcategories"
    response = requests.get(canvas_url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        subcategories = response.json()
        print(f"Found {len(subcategories)} Canvas subcategories:")
        
        for subcat in subcategories[:2]:  # Test first 2 subcategories
            print(f"\n--- {subcat['name']} (ID: {subcat['subcategoryId']}) ---")
            
            # Get options for this subcategory
            options_url = f"{base_url}/products/subcategories/{subcat['subcategoryId']}/options"
            options_response = requests.get(options_url, headers=headers, timeout=30)
            
            if options_response.status_code == 200:
                options = options_response.json()
                print(f"Options: {json.dumps(options, indent=2)}")
            else:
                print(f"Failed to get options: {options_response.status_code}")
                
    else:
        print(f"Failed to get subcategories: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
