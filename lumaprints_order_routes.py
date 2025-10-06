"""
Flask routes for Lumaprints order processing
Add these routes to your main app.py file
"""

from flask import request, jsonify, render_template, redirect, url_for
import json
import os
import uuid
from datetime import datetime
from lumaprints_api import get_lumaprints_client

# Order storage (in production, use a proper database)
ORDERS_FILE = os.path.join(os.path.dirname(__file__), 'orders.json')

def load_orders():
    """Load orders from JSON file"""
    try:
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_orders(orders):
    """Save orders to JSON file"""
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

@app.route('/order-print')
def order_print_form():
    """
    Display the order form for a specific product configuration
    
    Query parameters:
    - image: image filename
    - title: image title
    - subcategory_id: product subcategory ID
    - width: print width
    - height: print height
    - quantity: quantity (default 1)
    - price: total price
    """
    try:
        # Get parameters from query string
        image_filename = request.args.get('image', '')
        image_title = request.args.get('title', 'Untitled')
        subcategory_id = int(request.args.get('subcategory_id', 0))
        width = float(request.args.get('width', 0))
        height = float(request.args.get('height', 0))
        quantity = int(request.args.get('quantity', 1))
        price = float(request.args.get('price', 0))
        options = request.args.get('options', '[]')
        
        # Parse options
        try:
            options = json.loads(options)
        except:
            options = []
        
        # Validate required parameters
        if not all([image_filename, subcategory_id, width, height, price]):
            return "Missing required parameters", 400
        
        # Load catalog to get product names
        catalog_path = os.path.join(os.path.dirname(__file__), 'lumaprints_catalog.json')
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
        
        # Find product and subcategory names
        product_name = "Unknown Product"
        size_name = "Custom Size"
        
        for category in catalog['categories']:
            subcategories = catalog['subcategories'].get(str(category['id']), [])
            for subcat in subcategories:
                if subcat['subcategoryId'] == subcategory_id:
                    product_name = category['name']
                    size_name = subcat['name']
                    break
        
        # Construct image URL
        image_url = f"/static/assets/{image_filename}"
        
        # Render order form
        return render_template('lumaprints_order_form.html',
            image_url=image_url,
            image_title=image_title,
            product_name=product_name,
            size_name=size_name,
            width=width,
            height=height,
            quantity=quantity,
            formatted_price=f"${price:.2f}",
            subcategory_id=subcategory_id,
            options=options,
            price=price
        )
        
    except Exception as e:
        return f"Error loading order form: {str(e)}", 500

@app.route('/api/lumaprints/submit-order', methods=['POST'])
def submit_lumaprints_order():
    """
    Submit an order to Lumaprints and store locally
    
    Expected JSON payload:
    {
        "subcategoryId": 101001,
        "width": 16,
        "height": 20,
        "quantity": 1,
        "options": [],
        "imageUrl": "/static/assets/image.jpg",
        "price": 89.99,
        "shipping": {
            "firstName": "John",
            "lastName": "Doe",
            "addressLine1": "123 Main St",
            "addressLine2": "",
            "city": "Anytown",
            "state": "CA",
            "zipCode": "12345",
            "country": "US",
            "phone": "555-1234",
            "email": "john@example.com"
        },
        "payment": {
            "method": "PayPal",
            "transactionId": "PAYPAL_TXN_ID",
            "status": "COMPLETED"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subcategoryId', 'width', 'height', 'quantity', 'imageUrl', 'price', 'shipping', 'payment']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate order ID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # Create order record
        order_record = {
            'orderId': order_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'product': {
                'subcategoryId': data['subcategoryId'],
                'width': data['width'],
                'height': data['height'],
                'quantity': data['quantity'],
                'options': data.get('options', [])
            },
            'image': {
                'url': data['imageUrl'],
                'filename': os.path.basename(data['imageUrl'])
            },
            'pricing': {
                'total': data['price']
            },
            'shipping': data['shipping'],
            'payment': data['payment'],
            'lumaprints': {
                'orderId': None,
                'status': None,
                'submitted': False
            }
        }
        
        # Store order locally
        orders = load_orders()
        orders[order_id] = order_record
        save_orders(orders)
        
        # Submit to Lumaprints API
        try:
            api = get_lumaprints_client(sandbox=True)
            
            # Convert local image URL to full URL
            image_url = data['imageUrl']
            if image_url.startswith('/static/'):
                # Convert to full URL - you'll need to update this with your actual domain
                image_url = f"https://fifth-element-photography-production.up.railway.app{image_url}"
            
            # Prepare Lumaprints order payload
            lumaprints_payload = {
                "externalId": order_id,
                "storeId": "20027",  # Your store ID from catalog
                "shippingMethod": "default",
                "productionTime": "regular",
                "recipient": {
                    "firstName": data['shipping']['firstName'],
                    "lastName": data['shipping']['lastName'],
                    "addressLine1": data['shipping']['addressLine1'],
                    "addressLine2": data['shipping'].get('addressLine2', ''),
                    "city": data['shipping']['city'],
                    "state": data['shipping']['state'],
                    "zipCode": data['shipping']['zipCode'],
                    "country": data['shipping']['country'],
                    "phone": data['shipping'].get('phone', ''),
                    "company": ""
                },
                "orderItems": [{
                    "externalItemId": f"{order_id}-1",
                    "subcategoryId": data['subcategoryId'],
                    "quantity": data['quantity'],
                    "width": data['width'],
                    "height": data['height'],
                    "file": {
                        "imageUrl": image_url
                    },
                    "orderItemOptions": data.get('options', []),
                    "solidColorHexCode": None
                }]
            }
            
            # Submit order to Lumaprints
            lumaprints_response = api.submit_order(lumaprints_payload)
            
            # Update order record with Lumaprints response
            order_record['lumaprints'] = {
                'orderId': lumaprints_response.get('orderId'),
                'status': lumaprints_response.get('status'),
                'submitted': True,
                'response': lumaprints_response
            }
            order_record['status'] = 'submitted'
            
            # Save updated order
            orders[order_id] = order_record
            save_orders(orders)
            
        except Exception as lumaprints_error:
            # Log the error but don't fail the order
            print(f"Lumaprints submission error: {lumaprints_error}")
            order_record['lumaprints']['error'] = str(lumaprints_error)
            order_record['status'] = 'payment_received'
            
            # Save order with error
            orders[order_id] = order_record
            save_orders(orders)
        
        return jsonify({
            'success': True,
            'orderId': order_id,
            'message': 'Order submitted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    """
    Display order confirmation page
    """
    try:
        orders = load_orders()
        order = orders.get(order_id)
        
        if not order:
            return "Order not found", 404
        
        return render_template('order_confirmation.html', order=order)
        
    except Exception as e:
        return f"Error loading order confirmation: {str(e)}", 500

@app.route('/admin/orders')
def admin_orders():
    """
    Admin page to view all orders
    """
    try:
        orders = load_orders()
        
        # Sort orders by timestamp (newest first)
        sorted_orders = sorted(orders.items(), 
                             key=lambda x: x[1]['timestamp'], 
                             reverse=True)
        
        return render_template('admin_orders.html', orders=sorted_orders)
        
    except Exception as e:
        return f"Error loading orders: {str(e)}", 500

@app.route('/api/lumaprints/order-status/<order_id>')
def get_order_status(order_id):
    """
    Get the status of a specific order
    """
    try:
        orders = load_orders()
        order = orders.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # If order was submitted to Lumaprints, check for updates
        if order['lumaprints']['submitted'] and order['lumaprints']['orderId']:
            try:
                api = get_lumaprints_client(sandbox=True)
                lumaprints_status = api.get_order(order['lumaprints']['orderId'])
                
                # Update local order status
                order['lumaprints']['status'] = lumaprints_status.get('status')
                orders[order_id] = order
                save_orders(orders)
                
            except Exception as e:
                print(f"Error checking Lumaprints status: {e}")
        
        return jsonify({
            'success': True,
            'order': order
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
