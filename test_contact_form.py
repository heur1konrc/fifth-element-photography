#!/usr/bin/env python3
"""Test script for contact form email functionality"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'rick@fifthelement.photos'
SMTP_PASSWORD = 'kkswloyimwvdekxn'

def test_email():
    """Send a test email to verify SMTP configuration"""
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL
        msg['Subject'] = 'Test: Fifth Element Photography Contact Form'
        
        html_body = """
        <html>
        <body>
            <h2>Contact Form Test</h2>
            <p>This is a test email from the Fifth Element Photography contact form system.</p>
            <p>If you're receiving this, the email configuration is working correctly!</p>
            <p><strong>Timestamp:</strong> {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        text_body = "Contact Form Test\n\nThis is a test email from the Fifth Element Photography contact form system.\nTimestamp: {}".format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        print("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("Starting TLS...")
            server.starttls()
            print("Logging in...")
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            print("Sending message...")
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        print(f"Check {SMTP_EMAIL} for the test message.")
        return True
    
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

if __name__ == '__main__':
    test_email()
