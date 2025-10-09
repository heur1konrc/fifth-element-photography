import requests
import json
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

# OrderDesk API Configuration
ORDERDESK_API_URL = "https://app.orderdesk.me/api/v2/orders"
ORDERDESK_STORE_ID = "YOUR_STORE_ID"  # Replace with your actual Store ID
ORDERDESK_API_KEY = "YOUR_API_KEY"    # Replace with your actual API Key

# Product mapping
PRODUCT_MAPPING = {
    "101001": {"name": "Canvas Print 0.75in (12x12)", "price": 25.00, "lumaprints_options": "1,5"},
    "106001": {"name": "Metal Print", "price": 35.00, "lumaprints_options": "29,31"},
    "103001": {"name": "Fine Art Paper", "price": 20.00, "lumaprints_options": "36"}
}

app = Flask(__name__)
app.secret_key = 'test_secret_key'

@app.route('/test_order_form')
def test_order_form():
    """Display the test order form"""
    return render_template('test_order_form.html')

@app.route('/test_order_submit', methods=['POST'])
def test_order_submit():
    """Submit test order to OrderDesk API"""
    try:
        # Get form data
        form_data = request.form
        product_sku = form_data.get('product_type')
        
        if product_sku not in PRODUCT_MAPPING:
            flash('Invalid product selected', 'error')
            return redirect(url_for('test_order_form'))
        
        product_info = PRODUCT_MAPPING[product_sku]
        
        # Prepare OrderDesk order data
        order_data = {
            "source_name": "Fifth Element Photography",
            "email": form_data.get('email'),
            "shipping": {
                "first_name": form_data.get('first_name'),
                "last_name": form_data.get('last_name'),
                "address1": form_data.get('address1'),
                "city": form_data.get('city'),
                "state": form_data.get('state'),
                "postal_code": form_data.get('postal_code'),
                "country": form_data.get('country'),
                "phone": form_data.get('phone', '')
            },
            "order_items": [
                {
                    "name": product_info["name"] + " - Yahara River Glass",
                    "price": product_info["price"],
                    "quantity": 1,
                    "weight": 1.0,
                    "code": product_sku,
                    "metadata": {
                        "print_sku": product_sku,
                        "print_url": "https://fifthelement.photos/images/12x12_Sparrow.jpg",
                        "print_width": "12",
                        "print_height": "12",
                        "lumaprints_options": product_info["lumaprints_options"]
                    }
                }
            ]
        }
        
        # Submit to OrderDesk API
        headers = {
            "ORDERDESK-STORE-ID": ORDERDESK_STORE_ID,
            "ORDERDESK-API-KEY": ORDERDESK_API_KEY,
            "Content-Type": "application/json"
        }
        
        print("Submitting order to OrderDesk...")
        print("Headers:", headers)
        print("Order Data:", json.dumps(order_data, indent=2))
        
        response = requests.post(ORDERDESK_API_URL, headers=headers, json=order_data)
        
        print("OrderDesk Response Status:", response.status_code)
        print("OrderDesk Response:", response.text)
        
        if response.status_code == 201:
            # Success
            order_response = response.json()
            flash(f'Order submitted successfully! OrderDesk Order ID: {order_response.get("id")}', 'success')
            return jsonify({
                "status": "success",
                "message": "Order submitted to OrderDesk successfully",
                "orderdesk_order_id": order_response.get("id"),
                "response": order_response
            })
        else:
            # Errors
            flash(f'Error submitting order: {response.text}', 'error')
            return jsonify({
                "status": "error",
                "message": f"OrderDesk API error: {response.status_code}",
                "response": response.text
            }), 400
            
    except Exception as e:
        print("Exception:", str(e))
        flash(f'Error: {str(e)}', 'error')
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
