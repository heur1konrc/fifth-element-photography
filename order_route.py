"""
Clean order form route for Fifth Element Photography
Uses dynamic Lumaprints API
"""
from flask import render_template, request

def order_form_route():
    """Display the order form with image selection"""
    image_url = request.args.get('image', '')
    
    if not image_url:
        # Default to a sample image if none provided
        image_url = '/images/Forest.jpg'
    
    # Ensure full URL if relative path
    if not image_url.startswith('http'):
        image_url = f"https://fifthelement.photos{image_url if image_url.startswith('/') else '/' + image_url}"
    
    return render_template('order_form.html', image_url=image_url)

