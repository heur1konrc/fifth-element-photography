#!/usr/bin/env python3
"""
Fetch actual canvas sizes from Lumaprints API
"""

import json
import os
from lumaprints_api import LumaprintsAPI

def fetch_canvas_sizes():
    """Fetch all available canvas sizes from Lumaprints API"""
    
    # Initialize API client (using sandbox for testing)
    api_key = os.getenv('LUMAPRINTS_API_KEY', 'test_key')
    api_secret = os.getenv('LUMAPRINTS_API_SECRET', 'test_secret')
    
    api = LumaprintsAPI(api_key, api_secret, sandbox=True)
    
    try:
        # Get Canvas category (ID: 101)
        print("Fetching Canvas subcategories...")
        subcategories = api.get_subcategories(101)
        
        canvas_sizes = {}
        
        for subcat in subcategories:
            subcat_id = subcat['id']
            subcat_name = subcat['name']
            
            print(f"Processing {subcat_name} (ID: {subcat_id})...")
            
            # For each subcategory, we need to determine available sizes
            # This might require checking pricing for different size combinations
            # or looking for size constraints in the subcategory data
            
            sizes = []
            
            # Try common canvas sizes within the constraints
            min_width = subcat.get('minWidth', 8)
            max_width = subcat.get('maxWidth', 48)
            min_height = subcat.get('minHeight', 10)
            max_height = subcat.get('maxHeight', 60)
            
            print(f"  Size constraints: {min_width}x{min_height} to {max_width}x{max_height}")
            
            # Generate common sizes within constraints
            common_sizes = [
                (8, 10), (8, 12), (9, 12), (10, 10), (10, 12), (10, 14), (10, 20),
                (11, 14), (11, 17), (12, 12), (12, 16), (12, 18), (12, 24),
                (14, 18), (16, 16), (16, 20), (16, 24), (18, 18), (18, 24),
                (20, 20), (20, 24), (20, 30), (24, 24), (24, 30), (24, 36),
                (30, 30), (30, 40), (36, 36), (36, 48), (40, 40), (40, 60),
                (45, 45), (45, 60), (48, 48), (48, 60)
            ]
            
            for width, height in common_sizes:
                if (min_width <= width <= max_width and 
                    min_height <= height <= max_height):
                    
                    # Try to get pricing to verify this size is available
                    try:
                        pricing = api.get_pricing(subcat_id, width, height, 1)
                        if pricing and 'price' in pricing:
                            sizes.append({
                                'width': width,
                                'height': height,
                                'size_string': f"{width}x{height}",
                                'wholesale_price': pricing.get('price', 0)
                            })
                            print(f"    ✓ {width}x{height} - ${pricing.get('price', 0)}")
                    except Exception as e:
                        print(f"    ✗ {width}x{height} - Error: {e}")
                        continue
            
            canvas_sizes[subcat_name] = {
                'subcategory_id': subcat_id,
                'constraints': {
                    'min_width': min_width,
                    'max_width': max_width,
                    'min_height': min_height,
                    'max_height': max_height
                },
                'available_sizes': sizes,
                'total_sizes': len(sizes)
            }
        
        # Save results
        with open('actual_canvas_sizes.json', 'w') as f:
            json.dump(canvas_sizes, f, indent=2)
        
        print(f"\nResults saved to actual_canvas_sizes.json")
        
        # Print summary
        print("\nSummary:")
        for name, data in canvas_sizes.items():
            print(f"{name}: {data['total_sizes']} sizes")
        
        return canvas_sizes
        
    except Exception as e:
        print(f"Error fetching canvas sizes: {e}")
        return None

if __name__ == "__main__":
    fetch_canvas_sizes()
