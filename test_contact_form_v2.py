#!/usr/bin/env python3
"""Test script for contact form email functionality - v2 with debugging"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import ssl

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL = 'rick@fifthelement.photos'
SMTP_PASSWORD = 'kkswloyimwvdekxn'

def test_email_v1():
    """Test with standard TLS connection (port 587)"""
    print("\n=== Testing with Port 587 (TLS/STARTTLS) ===")
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL
        msg['Subject'] = 'Test: Fifth Element Photography Contact Form (Port 587)'
        
        html_body = """
        <html>
        <body>
            <h2>Contact Form Test - Port 587</h2>
            <p>This is a test email from the Fifth Element Photography contact form system.</p>
            <p><strong>Timestamp:</strong> {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        text_body = "Contact Form Test - Port 587\n\nTimestamp: {}".format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.set_debuglevel(1)  # Enable debug output
        
        print("Starting TLS...")
        server.starttls()
        
        print(f"Logging in as: {SMTP_EMAIL}")
        print(f"Password length: {len(SMTP_PASSWORD)} characters")
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        
        print("Sending message...")
        server.send_message(msg)
        server.quit()
        
        print("\n✅ Test email sent successfully via Port 587!")
        return True
    
    except Exception as e:
        print(f"\n❌ Error with Port 587: {e}")
        return False

def test_email_v2():
    """Test with SSL connection (port 465)"""
    print("\n=== Testing with Port 465 (SSL) ===")
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL
        msg['Subject'] = 'Test: Fifth Element Photography Contact Form (Port 465)'
        
        html_body = """
        <html>
        <body>
            <h2>Contact Form Test - Port 465</h2>
            <p>This is a test email from the Fifth Element Photography contact form system.</p>
            <p><strong>Timestamp:</strong> {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        text_body = "Contact Form Test - Port 465\n\nTimestamp: {}".format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"Connecting to {SMTP_SERVER}:465...")
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context, timeout=10)
        server.set_debuglevel(1)  # Enable debug output
        
        print(f"Logging in as: {SMTP_EMAIL}")
        print(f"Password length: {len(SMTP_PASSWORD)} characters")
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        
        print("Sending message...")
        server.send_message(msg)
        server.quit()
        
        print("\n✅ Test email sent successfully via Port 465!")
        return True
    
    except Exception as e:
        print(f"\n❌ Error with Port 465: {e}")
        return False

if __name__ == '__main__':
    print("Testing Gmail SMTP Configuration")
    print(f"Email: {SMTP_EMAIL}")
    print(f"Server: {SMTP_SERVER}")
    
    # Try port 587 first
    success = test_email_v1()
    
    # If 587 fails, try 465
    if not success:
        print("\nPort 587 failed, trying Port 465...")
        success = test_email_v2()
    
    if success:
        print("\n✅ Email configuration is working!")
    else:
        print("\n❌ Both connection methods failed. Please check:")
        print("  1. 2-Step Verification is enabled")
        print("  2. App Password is correct")
        print("  3. Google Workspace settings allow SMTP")
