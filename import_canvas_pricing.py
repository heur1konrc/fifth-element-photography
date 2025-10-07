"""
Import Canvas pricing data into the pricing database
"""

import json
from pricing_data_manager import PricingDataManager

def main():
    # Load Canvas pricing data
    with open('canvas_pricing_data.json', 'r') as f:
        canvas_data = json.load(f)
    
    print(f"Loaded {len(canvas_data)} Canvas pricing entries")
    
    # Initialize pricing manager
    manager = PricingDataManager()
    
    # Import the data
    result = manager.import_pricing_data('lumaprints_website_canvas', canvas_data)
    print(f"Import result: {result}")
    
    # Test some lookups
    print("\n--- Testing Canvas Pricing Lookups ---")
    
    # Test 8x10 Canvas pricing
    pricing_125 = manager.get_pricing('Canvas', '8×10', '1.25IN STRETCHED CANVAS')
    if pricing_125:
        print(f"8×10 Canvas (1.25\"): Wholesale ${pricing_125['wholesale_price']}, Retail ${pricing_125['retail_price']:.2f}")
    
    pricing_15 = manager.get_pricing('Canvas', '8×10', '1.5IN STRETCHED CANVAS')
    if pricing_15:
        print(f"8×10 Canvas (1.5\"): Wholesale ${pricing_15['wholesale_price']}, Retail ${pricing_15['retail_price']:.2f}")
    
    pricing_rolled = manager.get_pricing('Canvas', '8×10', 'ROLLED CANVAS')
    if pricing_rolled:
        print(f"8×10 Canvas (Rolled): Wholesale ${pricing_rolled['wholesale_price']}, Retail ${pricing_rolled['retail_price']:.2f}")
    
    # Get summary
    summary = manager.get_pricing_summary()
    print(f"\n--- Database Summary ---")
    print(f"Total entries: {summary['total_entries']}")
    print(f"Categories: {summary['categories']}")
    print(f"Price range: ${summary['price_range']['min']:.2f} - ${summary['price_range']['max']:.2f}")
    print(f"Average price: ${summary['price_range']['average']:.2f}")
    
    # Get all sizes for Canvas
    canvas_sizes = manager.get_sizes_for_category('Canvas')
    print(f"\nAvailable Canvas sizes: {canvas_sizes[:10]}...")  # Show first 10
    
    # Get all subcategories for Canvas
    canvas_subcategories = manager.get_subcategories_for_category('Canvas')
    print(f"Canvas subcategories: {canvas_subcategories}")

if __name__ == "__main__":
    main()
