"""
Lumaprints Pricing Scraper
Scrapes wholesale pricing data from Lumaprints website and stores it for dynamic pricing
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import os

class LumaprintsPricingScraper:
    def __init__(self, db_path: str = "lumaprints_pricing.db"):
        """
        Initialize the pricing scraper
        
        Args:
            db_path: Path to SQLite database for storing pricing data
        """
        self.db_path = db_path
        self.base_url = "https://www.lumaprints.com"
        self.pricing_url = f"{self.base_url}/pricing/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing pricing data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create pricing table
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
                markup_percentage REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, subcategory, size)
            )
        ''')
        
        # Create scraping log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                products_updated INTEGER,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_pricing_page(self) -> Optional[BeautifulSoup]:
        """
        Fetch and parse the Lumaprints pricing page
        
        Returns:
            BeautifulSoup object of the pricing page or None if failed
        """
        try:
            response = requests.get(self.pricing_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            print(f"Error fetching pricing page: {e}")
            return None
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price text and extract numeric value
        
        Args:
            price_text: Text containing price (e.g., "$10.99", "n/a")
            
        Returns:
            Float price value or None if invalid
        """
        if not price_text or price_text.lower() in ['n/a', 'na', '']:
            return None
        
        # Remove currency symbols and extract number
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        return None
    
    def parse_size(self, size_text: str) -> tuple:
        """
        Parse size text and extract width/height dimensions
        
        Args:
            size_text: Size text (e.g., "8×10", "12×16")
            
        Returns:
            Tuple of (width, height) or (None, None) if invalid
        """
        if not size_text:
            return None, None
        
        # Handle various size formats
        size_patterns = [
            r'(\d+(?:\.\d+)?)×(\d+(?:\.\d+)?)',  # 8×10, 12.5×16.5
            r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)',  # 8 x 10, 12.5 x 16.5
            r'(\d+(?:\.\d+)?)″\s*×\s*(\d+(?:\.\d+)?)″',  # 8″ × 10″
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, size_text, re.IGNORECASE)
            if match:
                try:
                    width = float(match.group(1))
                    height = float(match.group(2))
                    return width, height
                except ValueError:
                    continue
        
        return None, None
    
    def scrape_pricing_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Scrape pricing data from all tables on the page
        
        Args:
            soup: BeautifulSoup object of the pricing page
            
        Returns:
            List of pricing dictionaries
        """
        pricing_data = []
        
        # Find all pricing tables
        tables = soup.find_all('table')
        
        for table in tables:
            # Try to identify the product category from nearby elements
            category = self.identify_table_category(table)
            if not category:
                continue
            
            # Parse table rows
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + data rows
                continue
            
            # Get header row to identify columns
            header_row = rows[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Process data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                row_data = [cell.get_text(strip=True) for cell in cells]
                
                # First column is usually the size
                size_text = row_data[0] if row_data else ""
                width, height = self.parse_size(size_text)
                
                # Process price columns
                for i, price_text in enumerate(row_data[1:], 1):
                    price = self.parse_price(price_text)
                    if price is not None:
                        subcategory = headers[i] if i < len(headers) else f"Option_{i}"
                        
                        pricing_data.append({
                            'category': category,
                            'subcategory': subcategory,
                            'size': size_text,
                            'width': width,
                            'height': height,
                            'wholesale_price': price
                        })
        
        return pricing_data
    
    def identify_table_category(self, table) -> Optional[str]:
        """
        Identify the product category for a pricing table
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            Category name or None if not identifiable
        """
        # Look for category indicators in nearby elements
        parent = table.parent
        for _ in range(5):  # Search up to 5 levels up
            if parent is None:
                break
            
            # Look for headings or category indicators
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading = parent.find(tag)
                if heading:
                    text = heading.get_text(strip=True).lower()
                    if any(keyword in text for keyword in ['canvas', 'metal', 'paper', 'frame', 'foam', 'peel', 'stick']):
                        return heading.get_text(strip=True)
            
            # Look for div classes or IDs that might indicate category
            if parent.get('class') or parent.get('id'):
                class_text = ' '.join(parent.get('class', []))
                id_text = parent.get('id', '')
                combined = f"{class_text} {id_text}".lower()
                
                if 'canvas' in combined:
                    return 'Canvas'
                elif 'metal' in combined:
                    return 'Metal'
                elif 'paper' in combined:
                    return 'Fine Art Paper'
                elif 'frame' in combined:
                    return 'Framed'
            
            parent = parent.parent
        
        return None
    
    def calculate_retail_price(self, wholesale_price: float, markup_percentage: float = 150.0) -> float:
        """
        Calculate retail price with markup
        
        Args:
            wholesale_price: Wholesale price from Lumaprints
            markup_percentage: Markup percentage (150.0 = 150% markup)
            
        Returns:
            Retail price with markup applied
        """
        return wholesale_price * (markup_percentage / 100.0)
    
    def save_pricing_data(self, pricing_data: List[Dict], markup_percentage: float = 150.0):
        """
        Save pricing data to database
        
        Args:
            pricing_data: List of pricing dictionaries
            markup_percentage: Markup percentage to apply
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated_count = 0
        
        for item in pricing_data:
            wholesale_price = item['wholesale_price']
            retail_price = self.calculate_retail_price(wholesale_price, markup_percentage)
            
            # Insert or update pricing data
            cursor.execute('''
                INSERT OR REPLACE INTO pricing 
                (category, subcategory, size, width, height, wholesale_price, retail_price, markup_percentage, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                item['category'],
                item['subcategory'],
                item['size'],
                item['width'],
                item['height'],
                wholesale_price,
                retail_price,
                markup_percentage
            ))
            updated_count += 1
        
        # Log the scraping session
        cursor.execute('''
            INSERT INTO scraping_log (status, products_updated)
            VALUES (?, ?)
        ''', ('success', updated_count))
        
        conn.commit()
        conn.close()
        
        print(f"Updated {updated_count} pricing records")
    
    def scrape_and_update_pricing(self, markup_percentage: float = 150.0) -> bool:
        """
        Complete scraping workflow: fetch, parse, and save pricing data
        
        Args:
            markup_percentage: Markup percentage to apply to wholesale prices
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("Fetching Lumaprints pricing page...")
            soup = self.fetch_pricing_page()
            if not soup:
                raise Exception("Failed to fetch pricing page")
            
            print("Parsing pricing tables...")
            pricing_data = self.scrape_pricing_tables(soup)
            if not pricing_data:
                raise Exception("No pricing data found")
            
            print(f"Found {len(pricing_data)} pricing entries")
            
            print("Saving pricing data to database...")
            self.save_pricing_data(pricing_data, markup_percentage)
            
            print("✅ Pricing update completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Pricing update failed: {e}")
            
            # Log the error
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scraping_log (status, products_updated, error_message)
                VALUES (?, ?, ?)
            ''', ('error', 0, str(e)))
            conn.commit()
            conn.close()
            
            return False
    
    def get_pricing(self, category: str, size: str, subcategory: str = None) -> Optional[Dict]:
        """
        Get pricing for a specific product configuration
        
        Args:
            category: Product category (e.g., "Canvas", "Metal")
            size: Product size (e.g., "8×10")
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
        cursor.execute('SELECT DISTINCT size FROM pricing WHERE category = ? ORDER BY size', (category,))
        sizes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sizes


def main():
    """Test the pricing scraper"""
    scraper = LumaprintsPricingScraper()
    
    # Run scraping
    success = scraper.scrape_and_update_pricing(markup_percentage=150.0)
    
    if success:
        # Test retrieval
        print("\n--- Testing Price Retrieval ---")
        categories = scraper.get_all_categories()
        print(f"Available categories: {categories}")
        
        if categories:
            category = categories[0]
            sizes = scraper.get_sizes_for_category(category)
            print(f"Sizes for {category}: {sizes[:5]}")  # Show first 5 sizes
            
            if sizes:
                pricing = scraper.get_pricing(category, sizes[0])
                if pricing:
                    print(f"Sample pricing: {pricing}")


if __name__ == "__main__":
    main()
