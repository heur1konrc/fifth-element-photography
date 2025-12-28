"""
Contact Form API Route
Handles contact form submissions and sends emails via Gmail SMTP
"""

from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

contact_form_bp = Blueprint('contact_form', __name__, url_prefix='/api/contact')

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'rick@fifthelement.photos'
SMTP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', 'bpuumdgnsowgufgu')  # Gmail App Password

@contact_form_bp.route('/submit', methods=['POST'])
def submit_contact_form():
    """Handle contact form submission and send email"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'can_text', 'interested_in']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Extract form data
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        can_text = data.get('can_text')
        interested_in = data.get('interested_in')
        other_text = data.get('other_text', '')
        event_date = data.get('event_date', '')
        how_heard = data.get('how_heard', [])
        
        # Format the "interested in" value for better readability
        interest_map = {
            'business-portraiture': 'Business Portraiture Shoot (head shots)',
            'family-portraiture': 'Family Portraiture',
            'pet-portraiture': 'Pet Portraiture',
            'corporate-event': 'Corporate Event',
            'sporting-event': 'Sporting Event',
            'real-estate': 'Real Estate Marketing Shoot',
            'product-marketing': 'Product Marketing Shoot',
            'artist-band': 'Artist/Band Promotional shoot',
            'other': 'Other'
        }
        interested_in_display = interest_map.get(interested_in, interested_in)
        
        # Format how_heard list
        how_heard_display = ', '.join(how_heard) if how_heard else 'Not specified'
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL
        msg['Subject'] = f'New Contact Form Submission from {name}'
        msg['Reply-To'] = email
        
        # Create HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #6799c2; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #000; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>New Contact Form Submission</h2>
                    <p>Fifth Element Photography</p>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">Name:</span>
                        <span class="value">{name}</span>
                    </div>
                    <div class="field">
                        <span class="label">Email:</span>
                        <span class="value"><a href="mailto:{email}">{email}</a></span>
                    </div>
                    <div class="field">
                        <span class="label">Phone:</span>
                        <span class="value"><a href="tel:{phone}">{phone}</a></span>
                    </div>
                    <div class="field">
                        <span class="label">Can we text that number?</span>
                        <span class="value">{can_text.upper()}</span>
                    </div>
                    <div class="field">
                        <span class="label">I am interested in:</span>
                        <span class="value">{interested_in_display}</span>
                    </div>
        """
        
        # Add "Other" text if provided
        if other_text:
            html_body += f"""
                    <div class="field">
                        <span class="label">Other (specified):</span>
                        <span class="value">{other_text}</span>
                    </div>
            """
        
        # Add event date if provided
        if event_date:
            html_body += f"""
                    <div class="field">
                        <span class="label">Date of Event or deadline:</span>
                        <span class="value">{event_date}</span>
                    </div>
            """
        
        # Add how they heard about the service
        html_body += f"""
                    <div class="field">
                        <span class="label">How did you hear about my services?</span>
                        <span class="value">{how_heard_display}</span>
                    </div>
                    <div class="footer">
                        <p>Submitted on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p>This message was sent from the Fifth Element Photography contact form.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_body = f"""
New Contact Form Submission
Fifth Element Photography

Name: {name}
Email: {email}
Phone: {phone}
Can we text that number? {can_text.upper()}

I am interested in: {interested_in_display}
"""
        
        if other_text:
            text_body += f"Other (specified): {other_text}\n"
        
        if event_date:
            text_body += f"Date of Event or deadline: {event_date}\n"
        
        text_body += f"\nHow did you hear about my services? {how_heard_display}\n"
        text_body += f"\n---\nSubmitted on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        if not SMTP_PASSWORD:
            return jsonify({'success': False, 'error': 'Email configuration not set up'}), 500
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        
        return jsonify({'success': True, 'message': 'Contact form submitted successfully'})
    
    except Exception as e:
        print(f"Error sending contact form email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
