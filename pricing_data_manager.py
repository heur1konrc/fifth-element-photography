"""
Pricing Data Manager for Lumaprints Integration
Processes, cleans, and manages scraped pricing data from Lumaprints
"""

import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PricingEntry:
    """Data class for a pricing entry"""
    category: str
    subcategory: str
    size: str
    width: float
    height: float
    wholesale_price: float
    retail_price: float
    markup_percentage: float
    last_updated: str = None

class PricingDataManager:
    def __init__(self, db_path: str = "lumaprints_pricing.db"):
        """
        Initialize the pricing data manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create pricing table with proper constraints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                size TEXT NOT NULL,
                width REAL,
                height REAL,
                wholesale_price REAL NOT NULL,
                retail_price REAL NOT NULL,
                markup_percentage REAL NOT NULL DEFAULT 150.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, subcategory, size)
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category_size 
            ON pricing(category, size)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_dimensions 
            ON pricing(width, height)
        ''')
        
        # Create data import log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                records_processed INTEGER,
                records_imported INTEGER,
                status TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def clean_category_name(self, category: str) -> str:
        """
        Clean and standardize category names
        
        Args:
            category: Raw category name
            
        Returns:
            Cleaned category name
        """
        if not category or category.startswith('Table_'):
            return None
        
        # Standardize category names
        category = category.strip().lower()
        
        if 'canvas' in category and 'framed' not in category:
            return 'Canvas'
        elif 'framed canvas' in category:
            return 'Framed Canvas'
        elif 'metal' in category:
            return 'Metal'
        elif 'fine art paper' in category and 'framed' not in category and 'foam' not in category:
            return 'Fine Art Paper'
        elif 'framed fine art paper' in category:
            return 'Framed Fine Art Paper'
        elif 'foam' in category and 'mounted' in category:
            return 'Foam-mounted Fine Art Paper'
        elif 'peel' in category and 'stick' in category:
            return 'Peel and Stick'
        
        return None
    
    def clean_subcategory_name(self, subcategory: str) -> str:
        """
        Clean and standardize subcategory names
        
        Args:
            subcategory: Raw subcategory name
            
        Returns:
            Cleaned subcategory name
        """
        if not subcategory:
            return 'Standard'
        
        subcategory = subcategory.strip()
        
        # Skip shipping-related subcategories
        if any(location in subcategory.lower() for location in ['to ca', 'to tx', 'to ny']):
            return None
        
        # Clean up common subcategory patterns
        if '1.25in' in subcategory.lower():
            return '1.25" Stretched Canvas'
        elif '1.5in' in subcategory.lower():
            return '1.5" Stretched Canvas'
        elif '0.75in' in subcategory.lower():
            return '0.75" Stretched Canvas'
        elif 'rolled' in subcategory.lower():
            return 'Rolled Canvas'
        elif 'standard' in subcategory.lower():
            return 'Standard'
        
        return subcategory
    
    def is_valid_pricing_entry(self, entry: Dict) -> bool:
        """
        Validate if an entry is a valid product pricing entry
        
        Args:
            entry: Pricing entry dictionary
            
        Returns:
            True if valid product pricing, False if shipping or invalid
        """
        # Skip entries without proper category
        if not entry.get('category') or entry['category'].startswith('Table_'):
            return False
        
        # Skip shipping-related entries
        subcategory = entry.get('subcategory', '')
        if any(location in subcategory.lower() for location in ['to ca', 'to tx', 'to ny']):
            return False
        
        # Must have valid price
        if not entry.get('wholesale_price') or entry['wholesale_price'] <= 0:
            return False
        
        # Must have valid dimensions
        if not entry.get('width') or not entry.get('height'):
            return False
        
        # Price should be reasonable (between $1 and $1000)
        price = entry['wholesale_price']
        if price < 1.0 or price > 1000.0:
            return False
        
        return True
    
    def process_raw_data(self, raw_data: List[Dict]) -> List[PricingEntry]:
        """
        Process and clean raw pricing data
        
        Args:
            raw_data: List of raw pricing dictionaries
            
        Returns:
            List of cleaned PricingEntry objects
        """
        processed_entries = []
        
        for entry in raw_data:
            # Validate entry
            if not self.is_valid_pricing_entry(entry):
                continue
            
            # Clean category and subcategory
            category = self.clean_category_name(entry.get('category', ''))
            subcategory = self.clean_subcategory_name(entry.get('subcategory', ''))
            
            if not category or not subcategory:
                continue
            
            # Create pricing entry
            pricing_entry = PricingEntry(
                category=category,
                subcategory=subcategory,
                size=entry['size'],
                width=entry['width'],
                height=entry['height'],
                wholesale_price=entry['wholesale_price'],
                retail_price=entry['wholesale_price'] * 2.5,  # 150% markup
                markup_percentage=150.0,
                last_updated=datetime.now().isoformat()
            )
            
            processed_entries.append(pricing_entry)
        
        return processed_entries
    
    def import_pricing_data(self, data_source: str, raw_data: List[Dict]) -> Dict:
        """
        Import pricing data into the database
        
        Args:
            data_source: Source of the data (e.g., "lumaprints_website")
            raw_data: List of raw pricing dictionaries
            
        Returns:
            Import statistics dictionary
        """
        # Process the raw data
        processed_entries = self.process_raw_data(raw_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            for entry in processed_entries:
                # Insert or update pricing data
                cursor.execute('''
                    INSERT OR REPLACE INTO pricing 
                    (category, subcategory, size, width, height, wholesale_price, retail_price, markup_percentage, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.category,
                    entry.subcategory,
                    entry.size,
                    entry.width,
                    entry.height,
                    entry.wholesale_price,
                    entry.retail_price,
                    entry.markup_percentage,
                    entry.last_updated
                ))
                imported_count += 1
            
            # Log the import
            cursor.execute('''
                INSERT INTO import_log (source, records_processed, records_imported, status, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data_source,
                len(raw_data),
                imported_count,
                'success',
                f'Successfully imported {imported_count} pricing entries'
            ))
            
            conn.commit()
            
            return {
                'status': 'success',
                'records_processed': len(raw_data),
                'records_imported': imported_count,
                'message': f'Successfully imported {imported_count} pricing entries'
            }
            
        except Exception as e:
            conn.rollback()
            
            # Log the error
            cursor.execute('''
                INSERT INTO import_log (source, records_processed, records_imported, status, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data_source,
                len(raw_data),
                0,
                'error',
                str(e)
            ))
            conn.commit()
            
            return {
                'status': 'error',
                'records_processed': len(raw_data),
                'records_imported': 0,
                'message': f'Import failed: {e}'
            }
            
        finally:
            conn.close()
    
    def get_pricing(self, category: str, size: str, subcategory: str = None) -> Optional[Dict]:
        """
        Get pricing for a specific product configuration
        
        Args:
            category: Product category
            size: Product size
            subcategory: Product subcategory (optional)
            
        Returns:
            Pricing dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if subcategory:
            cursor.execute('''
                SELECT * FROM pricing 
                WHERE category = ? AND size = ? AND subcategory = ?
                ORDER BY last_updated DESC LIMIT 1
            ''', (category, size, subcategory))
        else:
            cursor.execute('''
                SELECT * FROM pricing 
                WHERE category = ? AND size = ?
                ORDER BY last_updated DESC LIMIT 1
            ''', (category, size))
        
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
    
    def get_all_categories(self) -> List[str]:
        """Get all available product categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM pricing ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_sizes_for_category(self, category: str) -> List[str]:
        """Get all available sizes for a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT size FROM pricing WHERE category = ? ORDER BY width, height', (category,))
        sizes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sizes
    
    def get_subcategories_for_category(self, category: str) -> List[str]:
        """Get all subcategories for a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT subcategory FROM pricing WHERE category = ? ORDER BY subcategory', (category,))
        subcategories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return subcategories
    
    def get_pricing_summary(self) -> Dict:
        """Get summary statistics of pricing data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM pricing')
        total_count = cursor.fetchone()[0]
        
        # Get category counts
        cursor.execute('SELECT category, COUNT(*) FROM pricing GROUP BY category ORDER BY category')
        category_counts = dict(cursor.fetchall())
        
        # Get price ranges
        cursor.execute('SELECT MIN(wholesale_price), MAX(wholesale_price), AVG(wholesale_price) FROM pricing')
        price_stats = cursor.fetchone()
        
        # Get last update
        cursor.execute('SELECT MAX(last_updated) FROM pricing')
        last_updated = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_entries': total_count,
            'categories': category_counts,
            'price_range': {
                'min': price_stats[0],
                'max': price_stats[1],
                'average': price_stats[2]
            },
            'last_updated': last_updated
        }


def main():
    """Test the pricing data manager"""
    # Load the extracted data
    with open('/home/ubuntu/fifth-element-photography/extracted_pricing_data.json', 'r') as f:
        extracted_data = json.load(f)
    
    # Initialize manager
    manager = PricingDataManager()
    
    # Import the data (we need to get the actual pricing data from the browser extraction)
    # For now, let's create some sample data based on what we saw
    sample_data = [
        {
            'category': 'Canvas',
            'subcategory': '1.25IN STRETCHED CANVAS',
            'size': '8×10',
            'width': 8,
            'height': 10,
            'wholesale_price': 10.99
        },
        {
            'category': 'Canvas',
            'subcategory': '1.5IN STRETCHED CANVAS', 
            'size': '8×10',
            'width': 8,
            'height': 10,
            'wholesale_price': 12.09
        },
        {
            'category': 'Metal',
            'subcategory': 'Standard',
            'size': '8×10',
            'width': 8,
            'height': 10,
            'wholesale_price': 15.99
        }
    ]
    
    # Import sample data
    result = manager.import_pricing_data('test_data', sample_data)
    print(f"Import result: {result}")
    
    # Test retrieval
    pricing = manager.get_pricing('Canvas', '8×10', '1.25IN STRETCHED CANVAS')
    print(f"Sample pricing: {pricing}")
    
    # Get summary
    summary = manager.get_pricing_summary()
    print(f"Pricing summary: {summary}")


if __name__ == "__main__":
    main()
