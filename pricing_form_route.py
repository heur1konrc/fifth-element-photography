"""
Simple pricing form route
"""
from flask import Blueprint, render_template

pricing_form = Blueprint('pricing_form', __name__)

@pricing_form.route('/pricing')
def show_pricing_form():
    """Display the pricing configuration form"""
    return render_template('pricing_form.html')

