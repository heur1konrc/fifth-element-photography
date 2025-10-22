"""
OrderDesk API Integration
Handles order submission to OrderDesk after payment
"""

import requests
import json
from datetime import datetime

# OrderDesk API Configuration
ORDERDESK_STORE_ID = "125137"
ORDERDESK_API_KEY = "pXmXDSnjdoRsjPYWD6uU2CBCcKPgZUur7SDDSMUa6NR2R4v6mQ"
ORDERDESK_API_URL = f"https://app.orderdesk.com/api/v2/orders"


def create_order(customer_data, cart_items, payment_data):
    """
    Create an order in OrderDesk
    
    Args:
        customer_data: dict with customer info (email, name, address, phone)
        cart_items: list of cart items with product details
        payment_data: dict with payment info (amount, method, transaction_id)
    
    Returns:
        dict with success status and order_id or error message
    """
    try:
        # Build order items for OrderDesk
        order_items = []
        
        for item in cart_items:
            product = item['product']
            
            # Parse size (e.g., "12x16" -> width=12, height=16)
            size_parts = product['size'].split('x')
            width = int(size_parts[0])
            height = int(size_parts[1]) if len(size_parts) > 1 else width
            
            order_item = {
                "name": product['name'],
                "price": float(product['retail_price']),
                "quantity": item.get('quantity', 1),
                "weight": 1.0,
                "code": str(product['lumaprints_subcategory_id']),
                "metadata": {
                    "print_sku": str(product['lumaprints_subcategory_id']),
                    "print_url": item['image'],
                    "print_width": width,
                    "print_height": height,
                    "lumaprints_options": product.get('lumaprints_options', '') or ''
                }
            }
            order_items.append(order_item)
        
        # Build order payload
        order_payload = {
            "source_id": payment_data.get('transaction_id', f"WEB-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "email": customer_data['email'],
            "shipping_method": "Ground Economy",  # Default from OrderDesk settings
            "customer": {
                "first_name": customer_data.get('first_name', ''),
                "last_name": customer_data.get('last_name', ''),
                "company": customer_data.get('company', ''),
                "email": customer_data['email'],
                "phone": customer_data.get('phone', '')
            },
            "shipping_address": {
                "first_name": customer_data.get('first_name', ''),
                "last_name": customer_data.get('last_name', ''),
                "company": customer_data.get('company', ''),
                "address1": customer_data.get('address1', ''),
                "address2": customer_data.get('address2', ''),
                "city": customer_data.get('city', ''),
                "state": customer_data.get('state', ''),
                "postal_code": customer_data.get('postal_code', ''),
                "country": customer_data.get('country', 'US'),
                "phone": customer_data.get('phone', '')
            },
            "order_items": order_items,
            "payment": {
                "amount": float(payment_data['amount']),
                "method": payment_data.get('method', 'Credit Card'),
                "transaction_id": payment_data.get('transaction_id', ''),
                "status": "approved"
            }
        }
        
        # Send to OrderDesk API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ORDERDESK_API_KEY}"
        }
        
        response = requests.post(
            ORDERDESK_API_URL,
            headers=headers,
            json=order_payload,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            return {
                'success': True,
                'order_id': result.get('id'),
                'order_number': result.get('source_id'),
                'message': 'Order created successfully in OrderDesk'
            }
        else:
            return {
                'success': False,
                'error': f"OrderDesk API error: {response.status_code} - {response.text}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Network error communicating with OrderDesk: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error creating order: {str(e)}"
        }


def get_order_status(order_id):
    """
    Get order status from OrderDesk
    
    Args:
        order_id: OrderDesk order ID
    
    Returns:
        dict with order status and details
    """
    try:
        headers = {
            "Authorization": f"Bearer {ORDERDESK_API_KEY}"
        }
        
        response = requests.get(
            f"{ORDERDESK_API_URL}/{order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            order = response.json()
            return {
                'success': True,
                'order': order
            }
        else:
            return {
                'success': False,
                'error': f"OrderDesk API error: {response.status_code}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"Error getting order status: {str(e)}"
        }


def handle_shipment_webhook(webhook_data):
    """
    Handle shipment notification webhook from OrderDesk/Lumaprints
    
    Args:
        webhook_data: dict with shipment notification data
    
    Returns:
        dict with success status
    """
    try:
        # Extract shipment info
        order_id = webhook_data.get('order_id')
        tracking_number = webhook_data.get('tracking_number')
        carrier = webhook_data.get('carrier')
        
        # TODO: Update order status in your database
        # TODO: Send shipment notification email to customer
        
        print(f"Shipment notification received for order {order_id}")
        print(f"Tracking: {carrier} - {tracking_number}")
        
        return {
            'success': True,
            'message': 'Shipment notification processed'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error processing shipment webhook: {str(e)}"
        }

