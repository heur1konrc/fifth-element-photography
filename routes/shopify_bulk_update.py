from flask import Blueprint, jsonify, render_template
import requests
import time
import os

shopify_bulk_update_bp = Blueprint('shopify_bulk_update', __name__, url_prefix='/admin')

SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

@shopify_bulk_update_bp.route('/shopify/bulk-remove-quotes', methods=['GET'])
def bulk_remove_quotes_page():
    """Display admin UI for bulk quote removal"""
    return render_template('admin/bulk_remove_quotes.html')

@shopify_bulk_update_bp.route('/api/shopify/bulk-remove-quotes', methods=['POST'])
def bulk_remove_quotes():
    """Bulk update all Shopify products to remove quotes from option values"""
    try:
        updated_products = []
        errors = []
        
        # Fetch all products (paginated)
        url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json'
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': SHOPIFY_API_SECRET
        }
        
        params = {'limit': 250}  # Max per page
        
        while url:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch products: {response.text}'
                }), 500
            
            products = response.json().get('products', [])
            
            for product in products:
                product_id = product['id']
                product_title = product['title']
                needs_update = False
                
                # Check if any option values contain quotes
                updated_options = []
                for option in product.get('options', []):
                    option_values = option.get('values', [])
                    updated_values = []
                    
                    for value in option_values:
                        if '"' in value:
                            needs_update = True
                            updated_values.append(value.replace('"', ''))
                        else:
                            updated_values.append(value)
                    
                    updated_options.append({
                        'id': option['id'],
                        'name': option['name'],
                        'values': updated_values
                    })
                
                # Update product if needed
                if needs_update:
                    # Also update variant option values
                    updated_variants = []
                    for variant in product.get('variants', []):
                        updated_variant = {
                            'id': variant['id']
                        }
                        
                        # Update option values for this variant
                        if variant.get('option1'):
                            updated_variant['option1'] = variant['option1'].replace('"', '')
                        if variant.get('option2'):
                            updated_variant['option2'] = variant['option2'].replace('"', '')
                        if variant.get('option3'):
                            updated_variant['option3'] = variant['option3'].replace('"', '')
                        
                        updated_variants.append(updated_variant)
                    
                    update_data = {
                        'product': {
                            'id': product_id,
                            'options': updated_options,
                            'variants': updated_variants
                        }
                    }
                    
                    # Update via API
                    update_url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products/{product_id}.json'
                    update_response = requests.put(update_url, headers=headers, json=update_data)
                    
                    if update_response.status_code == 200:
                        updated_products.append(product_title)
                    else:
                        errors.append(f'{product_title}: {update_response.text}')
                    
                    # Rate limiting: Shopify allows 2 requests per second
                    time.sleep(0.5)
            
            # Check for next page
            link_header = response.headers.get('Link', '')
            if 'rel="next"' in link_header:
                # Extract next page URL from Link header
                next_link = [l.strip() for l in link_header.split(',') if 'rel="next"' in l]
                if next_link:
                    url = next_link[0].split(';')[0].strip('<>')
                    params = None  # URL already contains params
                else:
                    url = None
            else:
                url = None
        
        return jsonify({
            'success': True,
            'updated': len(updated_products),
            'products': updated_products,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
