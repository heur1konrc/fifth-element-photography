"""
Pictorem API Integration Module
Handles all interactions with Pictorem API including pricing, orders, and caching
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta
from functools import wraps

DB_PATH = '/data/pictorem.db'

class PictoremAPI:
    def __init__(self):
        self.db_path = DB_PATH
        self.load_settings()
    
    def load_settings(self):
        """Load API settings from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT key_name, value FROM pictorem_settings')
        settings = {row['key_name']: row['value'] for row in cursor.fetchall()}
        
        self.api_token = settings.get('api_token', '')
        self.api_base_url = settings.get('api_base_url', 'https://www.pictorem.com/artflow')
        self.default_country = settings.get('default_country', 'USA')
        self.cache_ttl = int(settings.get('pricing_cache_ttl', 300))
        self.global_markup = float(settings.get('global_markup_percentage', 50))
        
        conn.close()
    
    def get_price(self, preorder_code, country=None, use_cache=True):
        """
        Get pricing for a product from Pictorem API
        
        Args:
            preorder_code: Pictorem preorder code string
            country: Country code (default: USA)
            use_cache: Whether to use cached pricing (default: True)
        
        Returns:
            dict with pricing information or None on error
        """
        if country is None:
            country = self.default_country
        
        # Check cache first
        if use_cache:
            cached_price = self._get_cached_price(preorder_code)
            if cached_price:
                return cached_price
        
        # Call API
        try:
            response = requests.post(
                f"{self.api_base_url}/getprice/",
                data={
                    "preordercode": preorder_code,
                    "deliverycountry": country
                },
                headers={
                    "artFlowKey": self.api_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status'):
                    price_data = data['worksheet']['price']
                    
                    # Extract pricing
                    base_price = price_data.get('total', 0)
                    price_breakdown = price_data.get('list', {})
                    
                    result = {
                        'base_price': base_price,
                        'customer_price': self._apply_markup(base_price),
                        'breakdown': price_breakdown,
                        'preorder_code': preorder_code
                    }
                    
                    # Cache the result
                    if use_cache:
                        self._cache_price(preorder_code, base_price, price_breakdown)
                    
                    return result
                else:
                    print(f"API Error: {data.get('msg', 'Unknown error')}")
                    return None
            else:
                print(f"HTTP Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def get_lead_time(self, preorder_code):
        """
        Get production lead time for a product
        
        Args:
            preorder_code: Pictorem preorder code string
        
        Returns:
            int: Lead time in business days, or None on error
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/getleadtime/",
                data={
                    "preordercode": preorder_code
                },
                headers={
                    "artFlowKey": self.api_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status'):
                    return data['data'].get('productionLeadTime', 5)
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def validate_preorder(self, preorder_code):
        """
        Validate a preorder code
        
        Args:
            preorder_code: Pictorem preorder code string
        
        Returns:
            dict with validation result or None on error
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/validatepreorder/",
                data={
                    "preordercode": preorder_code
                },
                headers={
                    "artFlowKey": self.api_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def build_preorder_code(self, product_slug, width, height, options=None):
        """
        Build a Pictorem preorder code from product selection
        
        Args:
            product_slug: Product slug from database
            width: Width in inches
            height: Height in inches
            options: Dict of additional options (moulding, mat, glazing, etc.)
        
        Returns:
            str: Pictorem preorder code
        """
        if options is None:
            options = {}
        
        # Get product template from database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT preorder_template FROM pictorem_products WHERE slug = ?', (product_slug,))
        product = cursor.fetchone()
        conn.close()
        
        if not product:
            return None
        
        template = product['preorder_template']
        
        # Determine orientation
        # Note: Pictorem uses horizontal for landscape (width > height)
        # and vertical for portrait (height > width)
        if int(width) > int(height):
            orientation = 'horizontal'
        elif int(height) > int(width):
            orientation = 'vertical'
        else:
            orientation = 'square'
        
        # Build replacement dict
        replacements = {
            'orientation': orientation,
            'width': str(width),
            'height': str(height),
            'moulding': options.get('moulding', '301-21'),
            'mat': options.get('mat', 'none'),
            'glazing': options.get('glazing', 'plexiglass'),
            'hanging': options.get('hanging', 'wire')
        }
        
        # Replace placeholders
        preorder_code = template
        for key, value in replacements.items():
            preorder_code = preorder_code.replace(f'{{{key}}}', value)
        
        return preorder_code
    
    def _apply_markup(self, base_price):
        """Apply markup percentage to base price"""
        multiplier = (self.global_markup / 100) + 1
        return round(base_price * multiplier, 2)
    
    def _get_cached_price(self, preorder_code):
        """Get cached price if available and not expired"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT base_price, price_breakdown, expires_at
            FROM pictorem_pricing_cache
            WHERE preorder_code = ? AND expires_at > datetime('now')
        ''', (preorder_code,))
        
        cached = cursor.fetchone()
        conn.close()
        
        if cached:
            breakdown = json.loads(cached['price_breakdown']) if cached['price_breakdown'] else {}
            return {
                'base_price': cached['base_price'],
                'customer_price': self._apply_markup(cached['base_price']),
                'breakdown': breakdown,
                'preorder_code': preorder_code,
                'cached': True
            }
        
        return None
    
    def _cache_price(self, preorder_code, base_price, breakdown):
        """Cache a price in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(seconds=self.cache_ttl)
        breakdown_json = json.dumps(breakdown) if breakdown else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO pictorem_pricing_cache 
            (preorder_code, base_price, price_breakdown, cached_at, expires_at)
            VALUES (?, ?, ?, datetime('now'), ?)
        ''', (preorder_code, base_price, breakdown_json, expires_at.isoformat()))
        
        conn.commit()
        conn.close()
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM pictorem_pricing_cache
            WHERE expires_at < datetime('now')
        ''')
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def update_markup(self, new_markup_percentage):
        """Update global markup percentage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE pictorem_settings
            SET value = ?, updated_at = datetime('now')
            WHERE key_name = 'global_markup_percentage'
        ''', (str(new_markup_percentage),))
        
        conn.commit()
        conn.close()
        
        # Reload settings
        self.load_settings()
        
        # Clear cache since prices changed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pictorem_pricing_cache')
        conn.commit()
        conn.close()


# Convenience functions for direct use

def get_product_price(product_slug, width, height, options=None):
    """
    Get price for a product configuration
    
    Args:
        product_slug: Product slug from database
        width: Width in inches
        height: Height in inches
        options: Dict of additional options
    
    Returns:
        dict with pricing or None
    """
    api = PictoremAPI()
    preorder_code = api.build_preorder_code(product_slug, width, height, options)
    
    if not preorder_code:
        return None
    
    return api.get_price(preorder_code)


def get_all_products():
    """Get all active products with categories"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            p.id,
            p.name,
            p.slug,
            p.material,
            p.type,
            p.description,
            c.name as category_name,
            c.slug as category_slug
        FROM pictorem_products p
        JOIN pictorem_categories c ON p.category_id = c.id
        WHERE p.active = 1 AND c.active = 1
        ORDER BY c.display_order, p.display_order
    ''')
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return products


def get_product_sizes(product_slug):
    """Get all sizes for a product with pricing"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            s.id as size_id,
            s.width, 
            s.height, 
            s.orientation, 
            s.display_name,
            pr.base_price,
            pr.customer_price,
            pr.markup_percentage,
            pr.last_synced
        FROM pictorem_sizes s
        JOIN pictorem_products p ON s.product_id = p.id
        LEFT JOIN pictorem_product_pricing pr ON (pr.size_id = s.id AND pr.product_id = p.id AND pr.option_id IS NULL)
        WHERE p.slug = ? AND s.active = 1
        ORDER BY s.display_order
    ''', (product_slug,))
    
    sizes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sizes


def get_product_options(product_slug, option_type=None):
    """Get options for a product"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if option_type:
        cursor.execute('''
            SELECT o.option_type, o.option_code, o.option_name, o.description
            FROM pictorem_product_options o
            JOIN pictorem_products p ON o.product_id = p.id
            WHERE p.slug = ? AND o.option_type = ? AND o.active = 1
            ORDER BY o.display_order
        ''', (product_slug, option_type))
    else:
        cursor.execute('''
            SELECT o.option_type, o.option_code, o.option_name, o.description
            FROM pictorem_product_options o
            JOIN pictorem_products p ON o.product_id = p.id
            WHERE p.slug = ? AND o.active = 1
            ORDER BY o.option_type, o.display_order
        ''', (product_slug,))
    
    options = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return options


if __name__ == '__main__':
    # Test the API
    print("Testing Pictorem API Integration...")
    print()
    
    api = PictoremAPI()
    
    # Test 1: Canvas pricing
    print("Test 1: Canvas 1.5\" - 24x30")
    price = get_product_price('stretched-canvas-15', 24, 30)
    if price:
        print(f"  Base Price: ${price['base_price']:.2f}")
        print(f"  Customer Price: ${price['customer_price']:.2f}")
        print(f"  Markup: {api.global_markup}%")
    print()
    
    # Test 2: Framed fine art pricing
    print("Test 2: Framed Fine Art - 24x18 with frame 301-21")
    price = get_product_price('framed-fine-art-print', 24, 18, {
        'moulding': '301-21',
        'glazing': 'plexiglass',
        'hanging': 'wire'
    })
    if price:
        print(f"  Base Price: ${price['base_price']:.2f}")
        print(f"  Customer Price: ${price['customer_price']:.2f}")
        print(f"  Breakdown: {price['breakdown']}")
    print()
    
    # Test 3: Metal print pricing
    print("Test 3: HD Metal - 20x24")
    price = get_product_price('metal-hd-chromaluxe', 20, 24)
    if price:
        print(f"  Base Price: ${price['base_price']:.2f}")
        print(f"  Customer Price: ${price['customer_price']:.2f}")
    print()
    
    print("✅ API Integration tests complete")

