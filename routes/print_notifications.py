"""
API routes for print availability notifications
"""
from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

print_notifications_bp = Blueprint('print_notifications', __name__)

@print_notifications_bp.route('/admin/notification-requests')
def admin_notification_requests():
    """Admin page to view notification requests"""
    from flask import render_template
    return render_template('notification_requests_admin.html')

@print_notifications_bp.route('/api/print-notifications/list', methods=['GET'])
def list_notifications():
    """API endpoint to list all notification requests"""
    try:
        from print_notifications_db import get_all_notification_requests
        requests = get_all_notification_requests()
        return jsonify({'success': True, 'requests': requests})
    except Exception as e:
        print(f"Error listing notification requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@print_notifications_bp.route('/api/print-notifications/mark-notified/<int:request_id>', methods=['POST'])
def mark_notified(request_id):
    """Mark a notification request as notified"""
    try:
        from print_notifications_db import mark_as_notified
        mark_as_notified(request_id)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error marking request as notified: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@print_notifications_bp.route('/api/print-notifications/delete/<int:request_id>', methods=['DELETE'])
def delete_notification(request_id):
    """Delete a notification request"""
    try:
        from print_notifications_db import delete_notification_request
        delete_notification_request(request_id)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting notification request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'rick@fifthelement.photos'
SMTP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')  # Gmail App Password
ADMIN_EMAIL = 'info@fifthelement.photos'

@print_notifications_bp.route('/api/print-notifications/request', methods=['POST'])
def request_notification():
    """Handle print availability notification request"""
    try:
        data = request.get_json()
        
        image_filename = data.get('image_filename')
        image_title = data.get('image_title', 'Untitled')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        
        # Validation
        if not image_filename:
            return jsonify({'success': False, 'error': 'Image filename is required'}), 400
        
        if not first_name or not last_name:
            return jsonify({'success': False, 'error': 'First and last name are required'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Valid email address is required'}), 400
        
        # Save to database
        from print_notifications_db import add_notification_request
        request_id = add_notification_request(image_filename, image_title, first_name, last_name, email)
        
        # Create customer in Shopify for email marketing
        shopify_result = create_shopify_customer_for_notification(first_name, last_name, email, image_title)
        
        # Send email to admin
        email_sent = send_admin_notification(image_filename, image_title, first_name, last_name, email, shopify_result)
        if not email_sent:
            print(f"Warning: Failed to send admin notification email for {image_title}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you! You will be notified when this print becomes available.',
            'request_id': request_id,
            'shopify_customer_created': shopify_result.get('success', False)
        })
        
    except Exception as e:
        print(f"Error processing notification request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_shopify_customer_for_notification(first_name, last_name, email, image_title):
    """Create customer in Shopify for email marketing purposes"""
    try:
        from shopify_customer import create_shopify_customer
        
        # Create customer with appropriate tags
        tags = ['Print Notification Request', f'Interested in: {image_title}']
        result = create_shopify_customer(first_name, last_name, email, tags)
        
        if result.get('success'):
            print(f"Shopify customer created/updated: {email} (ID: {result.get('customer_id')})")
        else:
            print(f"Failed to create Shopify customer: {result.get('error')}")
        
        return result
    except Exception as e:
        print(f"Exception creating Shopify customer: {e}")
        return {'success': False, 'error': str(e)}

def send_admin_notification(image_filename, image_title, first_name, last_name, email, shopify_result=None):
    """Send email notification to admin"""
    try:
        # Check if SMTP is configured
        if not SMTP_PASSWORD:
            print("SMTP password not configured, skipping email notification")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f'Print Availability Request: {image_title}'
        
        shopify_status = ''
        if shopify_result:
            if shopify_result.get('success'):
                if shopify_result.get('existing'):
                    shopify_status = f"\n\nShopify Status: Customer already exists (ID: {shopify_result.get('customer_id')})\nTags have been updated."
                else:
                    shopify_status = f"\n\nShopify Status: New customer created successfully (ID: {shopify_result.get('customer_id')})\nCustomer is now in your Shopify database for email marketing."
            else:
                shopify_status = f"\n\nShopify Status: Failed to create customer - {shopify_result.get('error')}"
        
        body = f"""
A customer has requested to be notified when a print becomes available for purchase.

Image Details:
- Filename: {image_filename}
- Title: {image_title}

Customer Information:
- Name: {first_name} {last_name}
- Email: {email}{shopify_status}

Action Required:
When you add this image to Shopify, remember to notify this customer at {email}.

You can view all pending notification requests in the Admin panel.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"Admin notification email sent successfully for {image_title}")
        return True
    except Exception as e:
        print(f"Error sending admin notification email: {e}")
        return False
