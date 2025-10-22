"""
Order API V3 - Clean implementation for new order form
Works directly with the rebuilt Lumaprints database
"""

from flask import jsonify, request, render_template
import sqlite3
import os
from PIL import Image
import requests
from io import BytesIO

DB_PATH = '/data/lumaprints_pricing.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def calculate_compatible_sizes(image_width, image_height, image_ratio, min_dpi=150):
    """
    Calculate which print sizes are compatible with the image
    based on dimensions and minimum DPI requirements
    """
    compatible_sizes = []
    
    # Common print sizes (in inches)
    standard_sizes = [
        (4, 6), (5, 7), (8, 10), (8, 12), (10, 20), (10, 30),
        (11, 14), (12, 12), (12, 16), (12, 18), (16, 20), (16, 24),
        (16, 48), (18, 24), (20, 20), (20, 40), (20, 60),
        (24, 30), (24, 36), (30, 30), (30, 40), (30, 60),
        (32, 48), (36, 48), (36, 72), (40, 40), (40, 60)
    ]
    
    for width_inches, height_inches in standard_sizes:
        # Check both orientations
        for w, h in [(width_inches, height_inches), (height_inches, width_inches)]:
            # Calculate required DPI
            dpi_w = image_width / w
            dpi_h = image_height / h
            min_dpi_for_size = min(dpi_w, dpi_h)
            
            # Check if DPI is sufficient
            if min_dpi_for_size >= min_dpi:
                # Check if aspect ratio is compatible (within 10% tolerance)
                size_ratio = w / h
                ratio_diff = abs(float(image_ratio) - size_ratio) / size_ratio
                
                if ratio_diff <= 0.10:  # 10% tolerance
                    size_str = f"{w}x{h}"
                    if size_str not in [s['size'] for s in compatible_sizes]:
                        compatible_sizes.append({
                            'size': size_str,
                            'width': w,
                            'height': h,
                            'dpi': round(min_dpi_for_size),
                            'ratio_match': round((1 - ratio_diff) * 100, 1)
                        })
    
    return compatible_sizes


def get_image_metadata(image_url):
    """
    Get image metadata from URL
    Returns width, height, and calculated DPI
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open with PIL
        img = Image.open(BytesIO(response.content))
        
        width, height = img.size
        ratio = round(width / height, 2)
        
        # Try to get DPI from image metadata
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
        print(f"Error getting image metadata: {e}")
        return None


def get_products_for_image(image_data):
    """
    Get compatible products from database based on image specifications
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate compatible sizes
        compatible_sizes = calculate_compatible_sizes(
            image_data['width'],
            image_data['height'],
            image_data['ratio']
        )
        
        if not compatible_sizes:
            return []
        
        # Get size strings for query
        size_list = [s['size'] for s in compatible_sizes]
        placeholders = ','.join(['?' for _ in size_list])
        
        # Query products
        query = f'''
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
            WHERE p.size IN ({placeholders})
                AND p.active = 1
            ORDER BY pt.display_order, c.display_order, p.size
        '''
        
        cursor.execute(query, size_list)
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
        return products
        
    except Exception as e:
        print(f"Error getting products: {e}")
        return []


def register_order_routes_v3(app):
    """Register V3 order form routes"""
    
    @app.route('/order')
    def order_form_v3():
        """Render the V3 order form"""
        return render_template('order_form_v3.html')
    
    @app.route('/api/order/products', methods=['POST'])
    def api_get_products():
        """API endpoint to get compatible products for an image"""
        try:
            data = request.json
            
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Image URL is required'
                }), 400
            
            # Get image metadata if not provided
            if 'width' not in data or 'height' not in data:
                metadata = get_image_metadata(data['url'])
                if not metadata:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to load image metadata'
                    }), 400
                data.update(metadata)
            
            # Get compatible products
            products = get_products_for_image(data)
            
            return jsonify({
                'success': True,
                'products': products,
                'image_data': {
                    'width': data['width'],
                    'height': data['height'],
                    'ratio': data['ratio'],
                    'dpi': data.get('dpi', 300)
                }
            })
            
        except Exception as e:
            print(f"Error in api_get_products: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/order/prepare', methods=['POST'])
    def api_prepare_order():
        """Prepare order data for OrderDesk format"""
        try:
            data = request.json
            
            # Validate cart
            if not data or 'items' not in data or len(data['items']) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Cart is empty'
                }), 400
            
            # Format items for OrderDesk
            order_items = []
            for item in data['items']:
                product = item['product']
                
                # Parse size (e.g., "12x16" -> width=12, height=16)
                size_parts = product['size'].split('x')
                width = int(size_parts[0])
                height = int(size_parts[1]) if len(size_parts) > 1 else width
                
                order_item = {
                    'name': product['name'],
                    'price': product['retail_price'],
                    'quantity': item.get('quantity', 1),
                    'weight': 1,  # Default weight
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
            print(f"Error in api_prepare_order: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/order/submit', methods=['POST'])
    def api_submit_order():
        """Submit order to OrderDesk after payment"""
        try:
            from orderdesk_integration import create_order
            
            data = request.json
            
            # Validate required fields
            required = ['customer', 'items', 'payment']
            for field in required:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # Submit to OrderDesk
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
            print(f"Error in api_submit_order: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/webhooks/orderdesk/shipment', methods=['POST'])
    def webhook_orderdesk_shipment():
        """Receive shipment notifications from OrderDesk"""
        try:
            from orderdesk_integration import handle_shipment_webhook
            
            data = request.json
            result = handle_shipment_webhook(data)
            
            return jsonify(result)
            
        except Exception as e:
            print(f"Error in webhook_orderdesk_shipment: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

