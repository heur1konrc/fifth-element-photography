"""
Realistic Pricing Calculator Based on Actual Lumaprints Wholesale Costs
Uses the real pricing table from Lumaprints with professional markup
"""

class RealisticPricingCalculator:
    def __init__(self, markup_multiplier=3.0):
        """
        Initialize with markup multiplier (3.0 = 300% markup = 3x wholesale)
        """
        self.markup_multiplier = markup_multiplier
        
        # Actual Lumaprints wholesale pricing from their table
        # Format: (width, height): wholesale_price
        self.wholesale_prices = {
            # Fine Art Paper (subcategory 103001)
            103001: {
                (4, 6): 1.71,
                (5, 7): 2.01,
                (8, 8): 2.79,
                (8, 10): 4.68,
                (8.5, 11): 3.54,
                (8, 12): 3.61,
                (10, 10): 3.68,
                (11, 14): 5.01,
                (11, 17): 5.81,
                (12, 12): 4.76,
                (12, 16): 5.92,
                (12, 24): 8.22,
                (12, 36): 11.69,
                (16, 16): 7.40,
                (16, 20): 8.89,
                (16, 24): 10.37,
            },
            
            # Canvas (subcategory 101001 - 0.75")
            101001: {
                (4, 6): 1.71,
                (5, 7): 2.01,
                (8, 8): 2.79,
                (8, 10): 3.19,
                (8.5, 11): 3.54,
                (8, 12): 3.61,
                (10, 10): 3.68,
                (11, 14): 5.01,
                (11, 17): 5.81,
                (12, 12): 4.76,
                (12, 16): 5.92,
                (12, 24): 8.22,
                (12, 36): 11.69,
                (16, 16): 7.40,
                (16, 20): 8.89,
                (16, 24): 10.37,
            },
            
            # Metal (subcategory 106001)
            106001: {
                (4, 6): 2.92,
                (5, 7): 3.61,
                (8, 8): 5.30,
                (8, 10): 6.22,
                (8.5, 11): 6.97,
                (8, 12): 7.12,
                (10, 10): 7.32,
                (11, 14): 10.25,
                (11, 17): 12.04,
                (12, 12): 9.70,
                (12, 16): 12.26,
                (12, 24): 17.40,
                (12, 36): 25.10,
                (16, 16): 15.56,
                (16, 20): 18.86,
                (16, 24): 22.16,
            }
        }
        
        # Product names for display
        self.product_names = {
            101001: "Canvas Print (0.75\")",
            101002: "Canvas Print (1.25\")",
            102001: "Framed Canvas", 
            103001: "Fine Art Paper",
            106001: "Metal Print",
        }
    
    def find_closest_size(self, subcategory_id, width, height):
        """
        Find the closest available size in the pricing table
        """
        if subcategory_id not in self.wholesale_prices:
            return None, None
            
        available_sizes = self.wholesale_prices[subcategory_id]
        target_area = width * height
        
        # Find the size with closest area
        closest_size = None
        closest_diff = float('inf')
        
        for (w, h), price in available_sizes.items():
            area = w * h
            diff = abs(area - target_area)
            if diff < closest_diff:
                closest_diff = diff
                closest_size = (w, h)
        
        if closest_size:
            return closest_size, available_sizes[closest_size]
        return None, None
    
    def calculate_retail_price(self, subcategory_id, width, height, quantity=1, options=None):
        """
        Calculate retail price based on actual Lumaprints wholesale costs
        """
        try:
            # Find closest size and wholesale price
            closest_size, wholesale_price = self.find_closest_size(subcategory_id, width, height)
            
            if wholesale_price is None:
                return {
                    'error': f'No pricing available for {width}×{height} in product type {subcategory_id}'
                }
            
            # Calculate retail price with markup
            retail_price = wholesale_price * self.markup_multiplier
            total_price = retail_price * quantity
            
            return {
                'success': True,
                'pricing': {
                    'retail_price': round(retail_price, 2),
                    'formatted_price': f'${retail_price:.2f}',
                    'wholesale_price': wholesale_price,
                    'total_price': round(total_price, 2),
                    'quantity': quantity,
                    'subcategory_id': subcategory_id,
                    'product_name': self.product_names.get(subcategory_id, f'Product {subcategory_id}'),
                    'dimensions': f'{width}" × {height}"',
                    'closest_size': f'{closest_size[0]}" × {closest_size[1]}"' if closest_size else None,
                    'markup_multiplier': self.markup_multiplier,
                    'markup_percentage': round((self.markup_multiplier - 1) * 100, 1)
                }
            }
            
        except Exception as e:
            return {
                'error': f'Pricing calculation failed: {str(e)}'
            }
    
    def get_available_sizes(self, subcategory_id=103001):
        """
        Get list of available sizes for a product type
        """
        if subcategory_id not in self.wholesale_prices:
            return []
            
        sizes = []
        for (width, height), price in self.wholesale_prices[subcategory_id].items():
            sizes.append({
                'width': width,
                'height': height,
                'display': f'{width}" × {height}"',
                'wholesale_price': price,
                'retail_price': round(price * self.markup_multiplier, 2)
            })
        
        # Sort by area (smallest to largest)
        sizes.sort(key=lambda x: x['width'] * x['height'])
        return sizes
    
    def get_available_products(self):
        """
        Get list of available products
        """
        return [
            {'id': 101001, 'name': 'Canvas Print (0.75")', 'category': 'Canvas'},
            {'id': 103001, 'name': 'Fine Art Paper', 'category': 'Paper'},
            {'id': 106001, 'name': 'Metal Print', 'category': 'Metal'},
        ]

def get_realistic_pricing_calculator(markup_multiplier=3.0):
    """
    Factory function to create a realistic pricing calculator
    """
    return RealisticPricingCalculator(markup_multiplier)
