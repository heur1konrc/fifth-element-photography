#!/usr/bin/env python3

import requests
import base64

# Test Lumaprints API authentication
API_KEY = "c5675f9b5bcab0799a49bba00da28405f2ca2ab72d31303137373136"
API_SECRET = "541614636cad6ba7f6be2d31303137373136"

# Create authentication header
credentials = f"{API_KEY}:{API_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

# Test sandbox URL
sandbox_url = "https://us.api-sandbox.lumaprints.com/api/v1/products/categories"

print("Testing Lumaprints API authentication...")
print(f"API Key: {API_KEY[:20]}...")
print(f"API Secret: {API_SECRET[:20]}...")
print(f"Encoded credentials: {encoded_credentials[:50]}...")
print(f"URL: {sandbox_url}")

try:
    response = requests.get(sandbox_url, headers=headers, timeout=30)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Got {len(data)} categories")
        for category in data[:3]:  # Show first 3 categories
            print(f"  - {category}")
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
