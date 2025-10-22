"""
Print Order API - Fresh implementation to bypass Railway caching
Created: 2025-10-22
All function names are NEW to force Railway to load fresh code
"""

from flask import jsonify, request, render_template
import sqlite3
import os
from PIL import Image

DB_PATH = '/data/lumaprints_pricing.db'

def connect_to_pricing_database():
    """Get database connection - NEW function name"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all_available_products():
    """
    Fetch ALL products from database without filtering
    NEW function name to bypass cache
    """
    try:
        conn = connect_to_pricing_database()
        cursor = conn.cursor()
        
        # Query ALL products - no filtering for now
        query = '''
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                p.retail_price,
                pt.name as product_type,
                c.name as category,
                p.lumaprints_subcategory_id,
                p.lumaprints_options
            FROM products p
            JOIN product_types pt ON p.product_type_id = pt.id
            JOIN categories c ON p.category_id = c.id
            WHERE p.active = 1
            ORDER BY pt.display_order, c.display_order, p.size
        '''
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            products.append({
                'id': row['id'],
                'name': row['name'],
                'size': row['size'],
                'cost_price': row['cost_price'],
                'retail_price': row['retail_price'],
                'product_type': row['product_type'],
                'category': row['category'],
                'lumaprints_subcategory_id': row['lumaprints_subcategory_id'],
                'lumaprints_options': row['lumaprints_options']
            })
        
        conn.close()
        print(f"✅ Successfully fetched {len(products)} products from database")
        return products
        
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_image_metadata(image_path):
    """
    Get image metadata from local file - NEW function name
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        ratio = round(width / height, 2)
        
        dpi = img.info.get('dpi', (300, 300))
        if isinstance(dpi, tuple):
            dpi = dpi[0]
        
        return {
            'width': width,
            'height': height,
            'ratio': ratio,
            'dpi': dpi
        }
    except Exception as e:
        print(f"Error extracting image metadata: {e}")
        return None


def setup_print_order_routes(app):
    """Register print order routes - NEW function name"""
    
    @app.route('/print-order')
    def render_print_order_form():
        """Render the print order form - NEW route"""
        return render_template('print_order_form.html')
    
    @app.route('/api/print-order/products', methods=['POST'])
    def fetch_products_for_print():
        """API endpoint to get products - NEW route and function name"""
        try:
            data = request.json
            
            # Image URL is required
            if 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Image URL is required'
                }), 400
            
            # Extract filename from URL
            image_url = data['url']
            filename = image_url.split('/')[-1]
            
            # Try to read from local filesystem
            local_paths = [
                f'/data/originals/{filename}',
                f'/data/{filename}',
                f'./data/originals/{filename}',
                f'./data/{filename}'
            ]
            
            metadata = None
            for path in local_paths:
                if os.path.exists(path):
                    metadata = extract_image_metadata(path)
                    if metadata:
                        print(f"✅ Read image from {path}: {metadata['width']}×{metadata['height']}")
                        break
            
            # Fallback to frontend dimensions
            if not metadata:
                print(f"⚠️  Using frontend dimensions")
                if 'width' in data and 'height' in data:
                    metadata = {
                        'width': data['width'],
                        'height': data['height'],
                        'ratio': data.get('ratio', data['width'] / data['height']),
                        'dpi': data.get('dpi', 300)
                    }
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Could not determine image dimensions'
                    }), 400
            
            # Get ALL products (no filtering)
            products = fetch_all_available_products()
            
            print(f"✅ Returning {len(products)} products to frontend")
            
            return jsonify({
                'success': True,
                'products': products,
                'image_data': metadata,
                'total_count': len(products)
            })
            
        except Exception as e:
            print(f"❌ Error in fetch_products_for_print: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/print-order/prepare', methods=['POST'])
    def prepare_print_order():
        """Prepare order data - NEW function name"""
        try:
            data = request.json
            
            if not data or 'items' not in data or len(data['items']) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Cart is empty'
                }), 400
            
            order_items = []
            for item in data['items']:
                product = item['product']
                
                size_parts = product['size'].split('x')
                width = int(size_parts[0])
                height = int(size_parts[1]) if len(size_parts) > 1 else width
                
                order_item = {
                    'name': product['name'],
                    'price': product['retail_price'],
                    'quantity': item.get('quantity', 1),
                    'weight': 1,
                    'metadata': {
                        'print_sku': product['lumaprints_subcategory_id'],
                        'print_url': item['image'],
                        'print_width': width,
                        'print_height': height,
                        'lumaprints_options': product['lumaprints_options'] or ''
                    }
                }
                order_items.append(order_item)
            
            return jsonify({
                'success': True,
                'order_items': order_items
            })
            
        except Exception as e:
            print(f"Error in prepare_print_order: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/print-order/submit', methods=['POST'])
    def submit_print_order():
        """Submit order to OrderDesk - NEW function name"""
        try:
            from orderdesk_integration import create_order
            
            data = request.json
            
            required = ['customer', 'items', 'payment']
            for field in required:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            result = create_order(
                customer_data=data['customer'],
                cart_items=data['items'],
                payment_data=data['payment']
            )
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Order submitted to OrderDesk',
                    'order_id': result['order_id'],
                    'order_number': result['order_number']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
            
        except Exception as e:
            print(f"Error in submit_print_order: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

