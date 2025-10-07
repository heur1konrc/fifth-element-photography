#!/usr/bin/env python3
"""
Test the API response format for frontend compatibility
"""

import json
from dynamic_pricing_calculator import get_dynamic_pricing_calculator

def test_api_format():
    calc = get_dynamic_pricing_calculator()
    result = calc.calculate_retail_price(101002, 8, 10, 1)
    
    # Format like the API would
    formatted = {
        'success': True,
        'pricing': {
            'formatted_price': f"${result['total_retail']:.2f}",
            'formatted_price_per_item': f"${result['price_per_item']:.2f}",
            'total_price': result['total_retail'],
            'price_per_item': result['price_per_item'],
            'wholesale_price': result['wholesale_price'],
            'quantity': result['quantity'],
            'markup_percentage': result['markup_percentage']
        },
        'product_info': {
            'subcategory_id': 101002,
            'category': result.get('category', ''),
            'subcategory': result.get('subcategory', ''),
            'width': 8,
            'height': 10
        }
    }
    
    print('API Response Format Test:')
    print(json.dumps(formatted, indent=2))
    
    print('\nFrontend expects:')
    print(f"- formatted_price: {formatted['pricing']['formatted_price']}")
    print(f"- formatted_price_per_item: {formatted['pricing']['formatted_price_per_item']}")
    
    return formatted

if __name__ == "__main__":
    test_api_format()
