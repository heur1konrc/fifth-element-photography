"""
Dynamic Pricing Calculator for Lumaprints Integration
Uses real-time pricing data from the database with automatic markup
"""

import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from pricing_data_manager import PricingDataManager

class DynamicPricingCalculator:
    def __init__(self, db_path: str = "lumaprints_pricing.db", markup_percentage: float = 150.0):
        """
        Initialize dynamic pricing calculator
        
        Args:
            db_path: Path to pricing database
            markup_percentage: Markup percentage (150.0 = 150% markup = 2.5x wholesale)
        """
        self.db_path = db_path
        self.markup_percentage = markup_percentage
        self.pricing_manager = PricingDataManager(db_path)
        
        # Subcategory ID to category mapping (from Lumaprints API)
        self.subcategory_mapping = {
            # Canvas subcategories
            101001: {'category': 'Canvas', 'subcategory': '0.75" Stretched Canvas'},
            101002: {'category': 'Canvas', 'subcategory': '1.25" Stretched Canvas'},
            101003: {'category': 'Canvas', 'subcategory': '1.5" Stretched Canvas'},
            101004: {'category': 'Canvas', 'subcategory': 'Rolled Canvas'},
            
            # Framed Canvas subcategories
            102001: {'category': 'Framed Canvas', 'subcategory': '0.75" Framed Canvas'},
            102002: {'category': 'Framed Canvas', 'subcategory': '1.25" Framed Canvas'},
            102003: {'category': 'Framed Canvas', 'subcategory': '1.5" Framed Canvas'},
            
            # Fine Art Paper subcategories
            103001: {'category': 'Fine Art Paper', 'subcategory': 'Standard'},
            
            # Framed Fine Art Paper subcategories
            104001: {'category': 'Framed Fine Art Paper', 'subcategory': 'Standard Frame'},
            
            # Foam-mounted Fine Art Paper subcategories
            105001: {'category': 'Foam-mounted Fine Art Paper', 'subcategory': 'Standard Mount'},
            
            # Metal subcategories
            106001: {'category': 'Metal', 'subcategory': 'Standard'},
            
            # Peel and Stick subcategories
            107001: {'category': 'Peel and Stick', 'subcategory': 'Standard'},
        }
    
    def find_closest_size(self, category: str, subcategory: str, target_width: float, target_height: float) -> Optional[Dict]:
        """
        Find the closest available size in the database
        
        Args:
            category: Product category
            subcategory: Product subcategory
            target_width: Target width in inches
            target_height: Target height in inches
            
        Returns:
            Pricing dictionary for closest size or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all available sizes for this category/subcategory
        cursor.execute('''
            SELECT * FROM pricing 
            WHERE category = ? AND subcategory = ?
            ORDER BY ABS(width - ?) + ABS(height - ?) ASC
            LIMIT 1
        ''', (category, subcategory, target_width, target_height))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'category': row[1],
                'subcategory': row[2],
                'size': row[3],
                'width': row[4],
                'height': row[5],
                'wholesale_price': row[6],
                'retail_price': row[7],
                'markup_percentage': row[8],
                'last_updated': row[9]
            }
        
        return None
    
    def calculate_size_adjustment(self, base_price: float, base_width: float, base_height: float, 
                                target_width: float, target_height: float) -> float:
        """
        Calculate price adjustment based on size difference
        
        Args:
            base_price: Base wholesale price
            base_width: Base width
            base_height: Base height
            target_width: Target width
            target_height: Target height
            
        Returns:
            Adjusted wholesale price
        """
        # Calculate area ratio
        base_area = base_width * base_height
        target_area = target_width * target_height
        area_ratio = target_area / base_area if base_area > 0 else 1.0
        
        # Apply square root scaling (price doesn't scale linearly with area)
        price_multiplier = area_ratio ** 0.7  # Slightly less than linear scaling
        
        return base_price * price_multiplier
    
    def calculate_retail_price(self, subcategory_id: int, width: float, height: float, 
                             quantity: int = 1, options: Optional[List[int]] = None) -> Dict:
        """
        Calculate retail price for a product configuration
        
        Args:
            subcategory_id: Lumaprints subcategory ID
            width: Print width in inches
            height: Print height in inches
            quantity: Number of prints
            options: List of option IDs (not used in current implementation)
            
        Returns:
            Pricing calculation result dictionary
        """
        try:
            # Map subcategory ID to category and subcategory
            if subcategory_id not in self.subcategory_mapping:
                return {
                    'error': f'Unknown subcategory ID: {subcategory_id}',
                    'wholesale_price': 0.0,
                    'retail_price': 0.0,
                    'quantity': quantity
                }
            
            mapping = self.subcategory_mapping[subcategory_id]
            category = mapping['category']
            subcategory = mapping['subcategory']
            
            # Try to find exact match first
            size_string = f"{int(width)}×{int(height)}"
            exact_pricing = self.pricing_manager.get_pricing(category, size_string, subcategory)
            
            if exact_pricing:
                # Exact match found
                wholesale_price = exact_pricing['wholesale_price']
                retail_price = exact_pricing['retail_price']
            else:
                # Find closest size and adjust
                closest_pricing = self.find_closest_size(category, subcategory, width, height)
                
                if closest_pricing:
                    # Calculate adjusted price based on size difference
                    base_wholesale = closest_pricing['wholesale_price']
                    adjusted_wholesale = self.calculate_size_adjustment(
                        base_wholesale, 
                        closest_pricing['width'], 
                        closest_pricing['height'],
                        width, 
                        height
                    )
                    wholesale_price = adjusted_wholesale
                    retail_price = wholesale_price * (self.markup_percentage / 100.0 + 1.0)
                else:
                    # Fallback to estimated pricing
                    area = width * height
                    estimated_wholesale = max(5.0, area * 0.8)  # Minimum $5, ~$0.80 per sq inch
                    wholesale_price = estimated_wholesale
                    retail_price = wholesale_price * (self.markup_percentage / 100.0 + 1.0)
            
            # Calculate total for quantity
            total_wholesale = wholesale_price * quantity
            total_retail = retail_price * quantity
            
            return {
                'subcategory_id': subcategory_id,
                'category': category,
                'subcategory': subcategory,
                'width': width,
                'height': height,
                'quantity': quantity,
                'wholesale_price': wholesale_price,
                'retail_price': retail_price,
                'total_wholesale': total_wholesale,
                'total_retail': total_retail,
                'markup_percentage': self.markup_percentage,
                'price_per_item': retail_price,
                'success': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'wholesale_price': 0.0,
                'retail_price': 0.0,
                'quantity': quantity,
                'success': False
            }
    
    def get_available_sizes(self, subcategory_id: int) -> List[Dict]:
        """
        Get all available sizes for a subcategory
        
        Args:
            subcategory_id: Lumaprints subcategory ID
            
        Returns:
            List of available size dictionaries
        """
        if subcategory_id not in self.subcategory_mapping:
            return []
        
        mapping = self.subcategory_mapping[subcategory_id]
        category = mapping['category']
        subcategory = mapping['subcategory']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT size, width, height, wholesale_price, retail_price 
            FROM pricing 
            WHERE category = ? AND subcategory = ?
            ORDER BY width, height
        ''', (category, subcategory))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'size': row[0],
                'width': row[1],
                'height': row[2],
                'wholesale_price': row[3],
                'retail_price': row[4]
            }
            for row in rows
        ]
    
    def update_markup_percentage(self, new_markup: float):
        """
        Update the markup percentage and recalculate all retail prices
        
        Args:
            new_markup: New markup percentage
        """
        self.markup_percentage = new_markup
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update all retail prices with new markup
        cursor.execute('''
            UPDATE pricing 
            SET retail_price = wholesale_price * (? / 100.0 + 1.0),
                markup_percentage = ?,
                last_updated = CURRENT_TIMESTAMP
        ''', (new_markup, new_markup))
        
        conn.commit()
        conn.close()
        
        print(f"Updated markup to {new_markup}% for all products")


def get_dynamic_pricing_calculator(markup_percentage: float = 150.0, db_path: str = None) -> DynamicPricingCalculator:
    """
    Get configured dynamic pricing calculator
    
    Args:
        markup_percentage: Markup percentage (150.0 = 150% markup)
        db_path: Path to pricing database (optional)
        
    Returns:
        Configured dynamic pricing calculator
    """
    if db_path is None:
        # Use default path in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, 'lumaprints_pricing.db')
    
    return DynamicPricingCalculator(db_path, markup_percentage)


def main():
    """Test the dynamic pricing calculator"""
    calc = get_dynamic_pricing_calculator(markup_percentage=150.0)
    
    # Test Canvas pricing
    print("Testing Canvas pricing...")
    result = calc.calculate_retail_price(101002, 8, 10, 1)  # 1.25" Canvas, 8x10
    print(f"8x10 Canvas (1.25\"): {result}")
    
    # Test with custom size
    result2 = calc.calculate_retail_price(101002, 9, 11, 2)  # Custom size
    print(f"9x11 Canvas (1.25\") x2: {result2}")
    
    # Test available sizes
    sizes = calc.get_available_sizes(101002)
    print(f"Available Canvas sizes: {len(sizes)} options")
    if sizes:
        print(f"Sample sizes: {sizes[:3]}")


if __name__ == "__main__":
    main()
