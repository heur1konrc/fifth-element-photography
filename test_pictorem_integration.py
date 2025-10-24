#!/usr/bin/env python3
"""
Test Pictorem Integration End-to-End
Verifies all components are working correctly
"""

import sys
import json
from pictorem_api import PictoremAPI, get_product_price, get_all_products, get_product_sizes, get_product_options
from pictorem_product_api import get_products_for_frontend, get_product_price_api, get_categories_for_frontend, get_product_details

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_database():
    """Test database connectivity and structure"""
    print_section("TEST 1: Database Connectivity")
    
    try:
        import sqlite3
        conn = sqlite3.connect('pictorem.db')
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'pictorem_categories',
            'pictorem_products',
            'pictorem_sizes',
            'pictorem_product_options',
            'pictorem_settings',
            'pictorem_pricing_cache'
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        print("✅ All required tables exist")
        
        # Check data exists
        cursor.execute("SELECT COUNT(*) FROM pictorem_categories WHERE active = 1")
        cat_count = cursor.fetchone()[0]
        print(f"✅ Categories: {cat_count}")
        
        cursor.execute("SELECT COUNT(*) FROM pictorem_products WHERE active = 1")
        prod_count = cursor.fetchone()[0]
        print(f"✅ Products: {prod_count}")
        
        cursor.execute("SELECT COUNT(*) FROM pictorem_sizes WHERE active = 1")
        size_count = cursor.fetchone()[0]
        print(f"✅ Sizes: {size_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_connection():
    """Test Pictorem API connection"""
    print_section("TEST 2: Pictorem API Connection")
    
    try:
        api = PictoremAPI()
        
        # Test simple canvas pricing
        test_code = '1|canvas|stretched|horizontal|24|30|mirrorimage|c15|regular'
        price = api.get_price(test_code, use_cache=False)
        
        if not price:
            print("❌ API connection failed - no response")
            return False
        
        print(f"✅ API connected successfully")
        print(f"   Test product: 24x30 Canvas 1.5\"")
        print(f"   Base price: ${price['base_price']:.2f}")
        print(f"   Customer price: ${price['customer_price']:.2f}")
        print(f"   Markup: {api.global_markup}%")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False

def test_preorder_code_builder():
    """Test preorder code building"""
    print_section("TEST 3: Preorder Code Builder")
    
    try:
        api = PictoremAPI()
        
        # Test canvas (30x24 is horizontal - width > height)
        code = api.build_preorder_code('stretched-canvas-15', 30, 24)
        expected = '1|canvas|stretched|horizontal|30|24|mirrorimage|c15|regular'
        if code != expected:
            print(f"❌ Canvas code mismatch")
            print(f"   Expected: {expected}")
            print(f"   Got: {code}")
            return False
        print(f"✅ Canvas code: {code}")
        
        # Test framed fine art
        code = api.build_preorder_code('framed-fine-art-print', 24, 18, {
            'moulding': '301-21',
            'glazing': 'plexiglass',
            'hanging': 'wire'
        })
        expected = '1|paper|art|horizontal|24|18|none|none|none|none|frame|301-21|plexiglass|wire'
        if code != expected:
            print(f"❌ Framed code mismatch")
            print(f"   Expected: {expected}")
            print(f"   Got: {code}")
            return False
        print(f"✅ Framed code: {code}")
        
        # Test metal (24x20 is horizontal - width > height)
        code = api.build_preorder_code('metal-hd-chromaluxe', 24, 20)
        expected = '1|metal|hd|horizontal|24|20'
        if code != expected:
            print(f"❌ Metal code mismatch")
            print(f"   Expected: {expected}")
            print(f"   Got: {code}")
            return False
        print(f"✅ Metal code: {code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Preorder code builder test failed: {e}")
        return False

def test_pricing_accuracy():
    """Test pricing calculations"""
    print_section("TEST 4: Pricing Accuracy")
    
    try:
        api = PictoremAPI()
        
        tests = [
            ('stretched-canvas-15', 24, 30, {}, 'Canvas 24x30'),
            ('framed-fine-art-print', 24, 18, {'moulding': '301-21', 'glazing': 'plexiglass', 'hanging': 'wire'}, 'Framed 24x18'),
            ('metal-hd-chromaluxe', 20, 24, {}, 'Metal 20x24'),
            ('acrylic-print-18', 16, 20, {}, 'Acrylic 16x20')
        ]
        
        for slug, width, height, options, name in tests:
            code = api.build_preorder_code(slug, width, height, options)
            if not code:
                print(f"❌ Failed to build code for {name}")
                return False
            
            price = api.get_price(code, use_cache=False)
            if not price:
                print(f"❌ Failed to get price for {name}")
                return False
            
            # Verify markup calculation
            expected_customer = price['base_price'] * (1 + api.global_markup / 100)
            if abs(price['customer_price'] - expected_customer) > 0.01:
                print(f"❌ Markup calculation error for {name}")
                print(f"   Base: ${price['base_price']:.2f}")
                print(f"   Expected: ${expected_customer:.2f}")
                print(f"   Got: ${price['customer_price']:.2f}")
                return False
            
            print(f"✅ {name}: ${price['base_price']:.2f} → ${price['customer_price']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pricing accuracy test failed: {e}")
        return False

def test_frontend_api():
    """Test frontend API endpoints"""
    print_section("TEST 5: Frontend API")
    
    try:
        # Test get_products_for_frontend
        from flask import Flask
        app = Flask(__name__)
        
        with app.app_context():
            response = get_products_for_frontend()
            data = response.get_json()
            
            if not data.get('success'):
                print(f"❌ get_products_for_frontend failed: {data.get('message')}")
                return False
            
            products = data.get('products', [])
            if len(products) == 0:
                print("❌ No products returned")
                return False
            
            print(f"✅ Products API: {len(products)} products returned")
            
            # Verify product structure
            first_product = products[0]
            required_fields = ['id', 'name', 'slug', 'category_name', 'product_type', 'sizes']
            missing_fields = [f for f in required_fields if f not in first_product]
            
            if missing_fields:
                print(f"❌ Missing fields in product: {missing_fields}")
                return False
            
            print(f"✅ Product structure valid")
            print(f"   Sample: {first_product['name']}")
            print(f"   Sizes: {len(first_product['sizes'])} available")
            
            # Test categories API
            response = get_categories_for_frontend()
            data = response.get_json()
            
            if not data.get('success'):
                print(f"❌ get_categories_for_frontend failed")
                return False
            
            categories = data.get('categories', [])
            print(f"✅ Categories API: {len(categories)} categories returned")
            
            # Test product details API
            response = get_product_details('stretched-canvas-15')
            data = response.get_json()
            
            if not data.get('success'):
                print(f"❌ get_product_details failed")
                return False
            
            product = data.get('product')
            print(f"✅ Product details API: {product['name']}")
            
            # Test pricing API
            response = get_product_price_api('stretched-canvas-15', 24, 30)
            data = response.get_json()
            
            if not data.get('success'):
                print(f"❌ get_product_price_api failed")
                return False
            
            print(f"✅ Pricing API: ${data['customer_price']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_caching():
    """Test pricing cache"""
    print_section("TEST 6: Pricing Cache")
    
    try:
        api = PictoremAPI()
        
        # Clear cache first
        import sqlite3
        conn = sqlite3.connect('pictorem.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pictorem_pricing_cache')
        conn.commit()
        conn.close()
        
        # First call (should hit API)
        code = '1|canvas|stretched|horizontal|24|30|mirrorimage|c15|regular'
        price1 = api.get_price(code, use_cache=True)
        
        if not price1:
            print("❌ First price call failed")
            return False
        
        print(f"✅ First call (API): ${price1['customer_price']:.2f}")
        
        # Second call (should use cache)
        price2 = api.get_price(code, use_cache=True)
        
        if not price2:
            print("❌ Second price call failed")
            return False
        
        if not price2.get('cached'):
            print("⚠️  Second call didn't use cache (may be OK if cache expired)")
        else:
            print(f"✅ Second call (cached): ${price2['customer_price']:.2f}")
        
        # Verify prices match
        if abs(price1['customer_price'] - price2['customer_price']) > 0.01:
            print("❌ Cached price doesn't match original")
            return False
        
        # Check cache entry exists
        conn = sqlite3.connect('pictorem.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM pictorem_pricing_cache WHERE preorder_code = ?', (code,))
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            print("❌ Cache entry not created")
            return False
        
        print(f"✅ Cache entry exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

def test_all_products():
    """Test pricing for all products"""
    print_section("TEST 7: All Products Pricing")
    
    try:
        api = PictoremAPI()
        products = get_all_products()
        
        print(f"Testing pricing for {len(products)} products...")
        
        failed = []
        for product in products:
            slug = product['slug']
            sizes = get_product_sizes(slug)
            
            if not sizes:
                print(f"⚠️  {product['name']}: No sizes available")
                continue
            
            # Test first size
            size = sizes[0]
            
            # Get options if needed
            if slug == 'framed-fine-art-print':
                options = {
                    'moulding': '301-21',
                    'glazing': 'plexiglass',
                    'hanging': 'wire'
                }
            else:
                options = {}
            
            code = api.build_preorder_code(slug, size['width'], size['height'], options)
            if not code:
                failed.append(f"{product['name']}: Code build failed")
                continue
            
            price = api.get_price(code)
            if not price:
                failed.append(f"{product['name']}: Pricing failed")
                continue
            
            print(f"  ✅ {product['name']} ({size['display_name']}): ${price['customer_price']:.2f}")
        
        if failed:
            print(f"\n❌ {len(failed)} products failed:")
            for f in failed:
                print(f"   - {f}")
            return False
        
        print(f"\n✅ All {len(products)} products priced successfully")
        return True
        
    except Exception as e:
        print(f"❌ All products test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("  PICTOREM INTEGRATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Database Connectivity", test_database),
        ("Pictorem API Connection", test_api_connection),
        ("Preorder Code Builder", test_preorder_code_builder),
        ("Pricing Accuracy", test_pricing_accuracy),
        ("Frontend API", test_frontend_api),
        ("Pricing Cache", test_caching),
        ("All Products Pricing", test_all_products)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - PICTOREM INTEGRATION READY")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed - review errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())

