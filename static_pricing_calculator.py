"""
Static Pricing Calculator for Lumaprints Products
Since Lumaprints doesn't have a pricing API, we calculate prices based on typical print costs
"""

class StaticPricingCalculator:
    def __init__(self, markup_percentage=100.0):
        """
        Initialize with markup percentage (100% = double the base cost)
        """
        self.markup_percentage = markup_percentage
        
        # Base pricing per square inch for different product types
        self.base_pricing = {
            101001: 0.85,  # Canvas Print (0.75")
            101002: 0.95,  # Canvas Print (1.25") 
            102001: 1.25,  # Framed Canvas
            103001: 0.65,  # Fine Art Paper
            106001: 1.15,  # Metal Print
        }
        
        # Product names for display
        self.product_names = {
            101001: "Canvas Print (0.75\")",
            101002: "Canvas Print (1.25\")",
            102001: "Framed Canvas", 
            103001: "Fine Art Paper",
            106001: "Metal Print",
        }
        
        # Size-based adjustments (larger sizes get slight discount per sq inch)
        self.size_adjustments = {
            (8, 10): 1.0,    # 8x10 - base price
            (11, 14): 0.95,  # 11x14 - 5% discount per sq inch
            (12, 16): 0.92,  # 12x16 - 8% discount per sq inch
            (16, 20): 0.88,  # 16x20 - 12% discount per sq inch
            (18, 24): 0.85,  # 18x24 - 15% discount per sq inch
            (20, 30): 0.82,  # 20x30 - 18% discount per sq inch
        }
    
    def calculate_retail_price(self, subcategory_id, width, height, quantity=1, options=None):
        """
        Calculate retail price for a product configuration
        
        Args:
            subcategory_id: Product type ID
            width: Width in inches
            height: Height in inches  
            quantity: Number of items
            options: Additional options (not used in static pricing)
            
        Returns:
            Dict with pricing information
        """
        try:
            # Get base price per square inch
            if subcategory_id not in self.base_pricing:
                return {
                    'error': f'Unknown product type: {subcategory_id}'
                }
            
            base_price_per_sq_inch = self.base_pricing[subcategory_id]
            
            # Calculate square inches
            square_inches = width * height
            
            # Apply size adjustment
            size_key = (width, height)
            size_adjustment = self.size_adjustments.get(size_key, 0.90)  # Default 10% discount for unlisted sizes
            
            # Calculate base cost
            base_cost = square_inches * base_price_per_sq_inch * size_adjustment
            
            # Apply markup
            retail_price = base_cost * (1 + self.markup_percentage / 100)
            
            # Calculate per-item price
            price_per_item = retail_price
            total_price = price_per_item * quantity
            
            return {
                'success': True,
                'subcategory_id': subcategory_id,
                'product_name': self.product_names.get(subcategory_id, f'Product {subcategory_id}'),
                'dimensions': f'{width}" × {height}"',
                'square_inches': square_inches,
                'quantity': quantity,
                'price_per_item': round(price_per_item, 2),
                'total_price': round(total_price, 2),
                'base_cost': round(base_cost, 2),
                'markup_percentage': self.markup_percentage,
                'size_adjustment': size_adjustment
            }
            
        except Exception as e:
            return {
                'error': f'Pricing calculation failed: {str(e)}'
            }
    
    def get_available_sizes(self):
        """
        Get list of available sizes
        """
        return [
            {'width': 8, 'height': 10, 'display': '8" × 10"'},
            {'width': 11, 'height': 14, 'display': '11" × 14"'},
            {'width': 12, 'height': 16, 'display': '12" × 16"'},
            {'width': 16, 'height': 20, 'display': '16" × 20"'},
            {'width': 18, 'height': 24, 'display': '18" × 24"'},
            {'width': 20, 'height': 30, 'display': '20" × 30"'},
        ]
    
    def get_available_products(self):
        """
        Get list of available products
        """
        return [
            {'id': 101001, 'name': 'Canvas Print (0.75")', 'category': 'Canvas'},
            {'id': 101002, 'name': 'Canvas Print (1.25")', 'category': 'Canvas'},
            {'id': 102001, 'name': 'Framed Canvas', 'category': 'Canvas'},
            {'id': 103001, 'name': 'Fine Art Paper', 'category': 'Paper'},
            {'id': 106001, 'name': 'Metal Print', 'category': 'Metal'},
        ]

def get_static_pricing_calculator(markup_percentage=100.0):
    """
    Factory function to create a static pricing calculator
    """
    return StaticPricingCalculator(markup_percentage)
