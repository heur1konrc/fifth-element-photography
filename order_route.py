"""
Clean order form route for Fifth Element Photography
Uses dynamic Lumaprints API
"""
from flask import render_template, request

def order_form_route():
    """Display the order form with image selection"""
    image_param = request.args.get('image', 'Forest.jpg')
    
    # Build image URL - must be full public URL for Lumaprints API
    if image_param.startswith('http'):
        # Already a full URL
        image_url = image_param
    else:
        # Convert relative path to full public URL
        if image_param.startswith('/images/'):
            relative_path = image_param
        elif image_param.startswith('/'):  
            relative_path = image_param
        else:
            # Just filename, prepend /images/
            relative_path = f"/images/{image_param}"
        
        # Get the base URL from the request
        base_url = request.host_url.rstrip('/')
        image_url = f"{base_url}{relative_path}"
    
    return render_template('order_form.html', image_url=image_url)

