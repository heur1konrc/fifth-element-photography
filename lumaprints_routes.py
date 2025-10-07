"""
Flask routes for Lumaprints integration
Add these routes to your main app.py file
"""

from flask import request, jsonify
import json
import os
from lumaprints_api import get_lumaprints_client, get_pricing_calculator

# Load product catalog
def load_catalog():
    """Load the Lumaprints product catalog"""
    catalog_path = os.path.join(os.path.dirname(__file__), 'lumaprints_catalog.json')
    try:
        with open(catalog_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"categories": [], "subcategories": {}, "options": {}, "stores": []}

# Initialize pricing calculator with 100% markup (double wholesale price)
pricing_calc = get_pricing_calculator(markup_percentage=100.0, sandbox=True)

@app.route('/api/lumaprints/catalog')
def get_lumaprints_catalog():
    """
    Get the complete Lumaprints product catalog
    Returns categories, subcategories, and options
    """
    try:
        catalog = load_catalog()
        return jsonify({
            'success': True,
            'catalog': catalog
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/categories')
def get_lumaprints_categories():
    """
    Get available product categories
    """
    try:
        catalog = load_catalog()
        return jsonify({
            'success': True,
            'categories': catalog.get('categories', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/subcategories/<int:category_id>')
def get_lumaprints_subcategories(category_id):
    """
    Get subcategories for a specific category
    """
    try:
        catalog = load_catalog()
        subcategories = catalog.get('subcategories', {}).get(str(category_id), [])
        return jsonify({
            'success': True,
            'subcategories': subcategories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/options/<int:subcategory_id>')
def get_lumaprints_options(subcategory_id):
    """
    Get options for a specific subcategory
    """
    try:
        catalog = load_catalog()
        options = catalog.get('options', {}).get(str(subcategory_id), [])
        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/pricing', methods=['POST'])
def get_lumaprints_pricing():
    """
    Calculate pricing for a specific product configuration
    
    Expected JSON payload:
    {
        "subcategoryId": 101001,
        "width": 16,
        "height": 20,
        "quantity": 1,
        "options": [11, 51, 23]  // optional
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subcategoryId', 'width', 'height']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        subcategory_id = data['subcategoryId']
        width = float(data['width'])
        height = float(data['height'])
        quantity = int(data.get('quantity', 1))
        options = data.get('options', [])
        
        # Calculate pricing
        pricing_result = pricing_calc.calculate_retail_price(
            subcategory_id=subcategory_id,
            width=width,
            height=height,
            quantity=quantity,
            options=options if options else None
        )
        
        if 'error' in pricing_result:
            return jsonify({
                'success': False,
                'error': pricing_result['error']
            }), 500
        
        # Format response
        response = {
            'success': True,
            'pricing': {
                'subcategoryId': subcategory_id,
                'width': width,
                'height': height,
                'quantity': quantity,
                'options': options,
                'wholesale_price': pricing_result['wholesale_price'],
                'markup_percentage': pricing_result['markup_percentage'],
                'markup_amount': pricing_result['markup_amount'],
                'retail_price': pricing_result['retail_price'],
                'price_per_item': pricing_result['price_per_item'],
                'formatted_price': f"${pricing_result['retail_price']:.2f}",
                'formatted_price_per_item': f"${pricing_result['price_per_item']:.2f}"
            }
        }
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/check-image', methods=['POST'])
def check_lumaprints_image():
    """
    Check if an image meets quality requirements for printing
    
    Expected JSON payload:
    {
        "imageUrl": "https://example.com/image.jpg",
        "subcategoryId": 101001,
        "width": 16,
        "height": 20
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['imageUrl', 'subcategoryId', 'width', 'height']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        api = get_lumaprints_client(sandbox=True)
        
        result = api.check_image(
            image_url=data['imageUrl'],
            subcategory_id=data['subcategoryId'],
            width=float(data['width']),
            height=float(data['height'])
        )
        
        return jsonify({
            'success': True,
            'image_check': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/popular-products')
def get_popular_products():
    """
    Get a curated list of popular products for quick selection
    """
    try:
        catalog = load_catalog()
        
        # Define popular product configurations
        popular_products = [
            {
                'name': '16×20 Canvas Print',
                'category': 'Canvas',
                'subcategoryId': 101001,  # 0.75in Stretched Canvas
                'width': 16,
                'height': 20,
                'description': 'Classic canvas print on 0.75" stretcher bars'
            },
            {
                'name': '11×14 Framed Canvas',
                'category': 'Framed Canvas', 
                'subcategoryId': 102001,  # 0.75in Framed Canvas
                'width': 11,
                'height': 14,
                'description': 'Canvas print with elegant frame'
            },
            {
                'name': '8×10 Fine Art Paper',
                'category': 'Fine Art Paper',
                'subcategoryId': 103001,  # Archival Matte Fine Art Paper
                'width': 8,
                'height': 10,
                'description': 'Museum-quality archival paper'
            },
            {
                'name': '12×18 Metal Print',
                'category': 'Metal',
                'subcategoryId': 106001,  # Glossy White Metal Print
                'width': 12,
                'height': 18,
                'description': 'Vibrant metal print with glossy finish'
            },
            {
                'name': '20×30 Canvas Print',
                'category': 'Canvas',
                'subcategoryId': 101002,  # 1.25in Stretched Canvas
                'width': 20,
                'height': 30,
                'description': 'Large canvas print on 1.25" stretcher bars'
            }
        ]
        
        # Calculate pricing for each popular product
        for product in popular_products:
            try:
                pricing = pricing_calc.calculate_retail_price(
                    subcategory_id=product['subcategoryId'],
                    width=product['width'],
                    height=product['height'],
                    quantity=1
                )
                product['price'] = pricing.get('retail_price', 0)
                product['formatted_price'] = f"${pricing.get('retail_price', 0):.2f}"
            except:
                product['price'] = 0
                product['formatted_price'] = "Price unavailable"
        
        return jsonify({
            'success': True,
            'popular_products': popular_products
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper function to get size recommendations based on image dimensions
@app.route('/api/lumaprints/size-recommendations', methods=['POST'])
def get_size_recommendations():
    """
    Get recommended print sizes based on image dimensions
    
    Expected JSON payload:
    {
        "imageWidth": 3000,
        "imageHeight": 2000,
        "subcategoryId": 101001
    }
    """
    try:
        data = request.get_json()
        
        image_width = int(data.get('imageWidth', 0))
        image_height = int(data.get('imageHeight', 0))
        subcategory_id = data.get('subcategoryId')
        
        if not image_width or not image_height:
            return jsonify({
                'success': False,
                'error': 'Image dimensions required'
            }), 400
        
        # Calculate aspect ratio
        aspect_ratio = image_width / image_height
        
        # Common print sizes that work well for photography
        common_sizes = [
            (8, 10), (8, 12), (11, 14), (12, 16), (16, 20), (16, 24), (20, 30)
        ]
        
        recommendations = []
        
        for width, height in common_sizes:
            # Check if size maintains reasonable aspect ratio
            size_ratio = width / height
            ratio_diff = abs(aspect_ratio - size_ratio)
            
            if ratio_diff < 0.3:  # Within reasonable aspect ratio range
                # Calculate DPI
                dpi_width = image_width / width
                dpi_height = image_height / height
                min_dpi = min(dpi_width, dpi_height)
                
                quality = "Excellent" if min_dpi >= 300 else "Good" if min_dpi >= 200 else "Fair" if min_dpi >= 150 else "Poor"
                
                if min_dpi >= 150:  # Only recommend if quality is Fair or better
                    recommendations.append({
                        'width': width,
                        'height': height,
                        'size_name': f'{width}×{height}',
                        'dpi': round(min_dpi),
                        'quality': quality,
                        'aspect_ratio_match': round((1 - ratio_diff) * 100)
                    })
        
        # Sort by quality (DPI) descending
        recommendations.sort(key=lambda x: x['dpi'], reverse=True)
        
        return jsonify({
            'success': True,
            'image_dimensions': {
                'width': image_width,
                'height': image_height,
                'aspect_ratio': round(aspect_ratio, 2)
            },
            'recommendations': recommendations[:6]  # Top 6 recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/lumaprints/submit-order', methods=['POST'])
def submit_lumaprints_order():
    """
    Submit an order to Lumaprints for fulfillment
    
    Expected JSON payload:
    {
        "customer": {
            "firstName": "John",
            "lastName": "Doe", 
            "email": "john@example.com",
            "phone": "555-123-4567"
        },
        "shipping": {
            "firstName": "John",
            "lastName": "Doe",
            "address1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postalCode": "12345",
            "country": "US"
        },
        "items": [
            {
                "subcategoryId": 101001,
                "width": 16,
                "height": 20,
                "quantity": 1,
                "imageUrl": "https://example.com/image.jpg",
                "options": [11, 51]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['customer', 'shipping', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate customer info
        customer = data['customer']
        required_customer_fields = ['firstName', 'lastName', 'email']
        for field in required_customer_fields:
            if field not in customer:
                return jsonify({
                    'success': False,
                    'error': f'Missing required customer field: {field}'
                }), 400
        
        # Validate shipping info
        shipping = data['shipping']
        required_shipping_fields = ['firstName', 'lastName', 'address1', 'city', 'state', 'postalCode', 'country']
        for field in required_shipping_fields:
            if field not in shipping:
                return jsonify({
                    'success': False,
                    'error': f'Missing required shipping field: {field}'
                }), 400
        
        # Validate items
        items = data['items']
        if not items or len(items) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one item is required'
            }), 400
        
        for i, item in enumerate(items):
            required_item_fields = ['subcategoryId', 'width', 'height', 'quantity', 'imageUrl']
            for field in required_item_fields:
                if field not in item:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field in item {i}: {field}'
                    }), 400
        
        # Get Lumaprints API client
        api = get_lumaprints_client(sandbox=True)
        
        # Get stores to find a valid store ID
        stores = api.get_stores()
        if not stores:
            return jsonify({
                'success': False,
                'error': 'No stores available'
            }), 500
        
        store_id = stores[0]['id']  # Use first available store
        
        # Prepare order payload for Lumaprints
        order_payload = {
            "storeId": store_id,
            "customer": {
                "firstName": customer['firstName'],
                "lastName": customer['lastName'],
                "email": customer['email'],
                "phone": customer.get('phone', '')
            },
            "shipping": {
                "firstName": shipping['firstName'],
                "lastName": shipping['lastName'],
                "address1": shipping['address1'],
                "address2": shipping.get('address2', ''),
                "city": shipping['city'],
                "state": shipping['state'],
                "postalCode": shipping['postalCode'],
                "country": shipping['country']
            },
            "items": []
        }
        
        # Process each item
        for item in items:
            order_item = {
                "subcategoryId": item['subcategoryId'],
                "width": float(item['width']),
                "height": float(item['height']),
                "quantity": int(item['quantity']),
                "imageUrl": item['imageUrl']
            }
            
            # Add options if provided
            if 'options' in item and item['options']:
                order_item['options'] = item['options']
            
            order_payload['items'].append(order_item)
        
        # Submit order to Lumaprints
        result = api.submit_order(order_payload)
        
        return jsonify({
            'success': True,
            'order': result,
            'message': 'Order submitted successfully to Lumaprints'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
