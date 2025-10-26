"""
Clean order form route for Fifth Element Photography
Uses dynamic Lumaprints API
"""
from flask import render_template, request

def order_form_route():
    """Display the order form with image selection"""
    image_param = request.args.get('image', 'Forest.jpg')
    
    # Build image URL
    if image_param.startswith('http'):
        image_url = image_param
    elif image_param.startswith('/images/'):
        image_url = image_param
    elif image_param.startswith('/'):  
        image_url = image_param
    else:
        # Just filename, prepend /images/
        image_url = f"/images/{image_param}"
    
    return render_template('order_form.html', image_url=image_url)

