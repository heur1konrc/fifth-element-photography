#!/usr/bin/env python3
"""Test Lumaprints API connection and pricing"""

from lumaprints_api import get_lumaprints_client

def test_api():
    print("🔌 Testing Lumaprints API connection...\n")
    
    # Initialize API client (production)
    api_client = get_lumaprints_client(sandbox=False)
    print("✅ API client initialized\n")
    
    # Test 1: Get categories
    print("📋 Test 1: Getting categories...")
    try:
        categories = api_client.get_categories()
        print(f"✅ Success! Found {len(categories)} categories")
        for cat in categories[:5]:
            print(f"   - {cat.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 2: Get pricing for Canvas 1.25" 8x10
    print("\n💰 Test 2: Getting pricing for Canvas 1.25\" 8×10\"...")
    try:
        pricing = api_client.get_pricing(
            subcategory_id=101002,  # 1.25" Canvas
            width=8,
            height=10,
            quantity=1
        )
        print(f"✅ Success! Price: ${pricing.get('price', 'N/A')}")
        print(f"   Full response: {pricing}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 3: Get pricing for Framed Fine Art
    print("\n🖼️  Test 3: Getting pricing for Framed Fine Art 0.875\" Black, No Mat, Archival Matte 8×10\"...")
    try:
        pricing = api_client.get_pricing(
            subcategory_id=105001,  # 0.875" Black Frame
            width=8,
            height=10,
            quantity=1,
            options=[64, 27]  # No Mat, Archival Matte
        )
        print(f"✅ Success! Price: ${pricing.get('price', 'N/A')}")
        print(f"   Full response: {pricing}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - API is working correctly!")
    print("="*60)
    return True

if __name__ == '__main__':
    test_api()

