"""
Fifth Element Photography - Shopify Customer Management
Creates customers in Shopify for email marketing purposes
Version: 1.0.0
"""

import os
import requests
import json
from datetime import datetime

# Shopify API credentials from environment
SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

def get_shopify_headers():
    """Get headers for Shopify API requests"""
    import base64
    auth_string = f"{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('ascii')
    
    return {
        'Authorization': f'Basic {base64_string}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def check_customer_exists(email):
    """
    Check if a customer already exists in Shopify by email
    
    Args:
        email (str): Customer email address
        
    Returns:
        dict: Customer data if exists, None otherwise
    """
    try:
        url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/customers/search.json"
        params = {'query': f'email:{email}'}
        headers = get_shopify_headers()
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            customers = data.get('customers', [])
            if customers:
                return customers[0]  # Return first matching customer
        elif response.status_code == 401:
            print(f"Shopify API authentication failed. Check credentials.")
            return None
        else:
            print(f"Shopify customer search failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error checking Shopify customer: {e}")
        return None
    
    return None

def create_shopify_customer(first_name, last_name, email, tags=None):
    """
    Create a new customer in Shopify
    
    Args:
        first_name (str): Customer's first name
        last_name (str): Customer's last name
        email (str): Customer's email address
        tags (list): Optional list of tags to apply to customer
        
    Returns:
        dict: Response with success status and customer data or error message
    """
    try:
        # Check if customer already exists
        existing_customer = check_customer_exists(email)
        if existing_customer:
            # Customer exists, optionally update tags
            customer_id = existing_customer.get('id')
            if tags:
                return update_customer_tags(customer_id, tags, existing_customer.get('tags', ''))
            return {
                'success': True,
                'customer_id': customer_id,
                'message': 'Customer already exists in Shopify',
                'existing': True
            }
        
        # Create new customer
        url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/customers.json"
        headers = get_shopify_headers()
        
        # Prepare customer data
        customer_data = {
            'customer': {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'verified_email': False,  # Email not verified yet
                'send_email_welcome': False,  # Don't send welcome email automatically
                'tags': ', '.join(tags) if tags else 'Print Notification Request',
                'note': f'Added via print notification system on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'accepts_marketing': True,  # Opt-in for marketing emails
                'marketing_opt_in_level': 'single_opt_in'
            }
        }
        
        response = requests.post(url, headers=headers, json=customer_data, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            customer = data.get('customer', {})
            return {
                'success': True,
                'customer_id': customer.get('id'),
                'message': 'Customer created successfully in Shopify',
                'existing': False
            }
        elif response.status_code == 422:
            # Validation error - customer might already exist
            error_data = response.json()
            errors = error_data.get('errors', {})
            if 'email' in errors and 'taken' in str(errors['email']):
                # Customer exists, try to find them
                existing_customer = check_customer_exists(email)
                if existing_customer:
                    return {
                        'success': True,
                        'customer_id': existing_customer.get('id'),
                        'message': 'Customer already exists in Shopify',
                        'existing': True
                    }
            return {
                'success': False,
                'error': f'Validation error: {errors}',
                'status_code': 422
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'error': 'Shopify API authentication failed. Check credentials.',
                'status_code': 401
            }
        else:
            return {
                'success': False,
                'error': f'Failed to create customer: {response.status_code} - {response.text}',
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Exception creating Shopify customer: {str(e)}'
        }

def update_customer_tags(customer_id, new_tags, existing_tags_str=''):
    """
    Update customer tags in Shopify (append new tags without removing existing ones)
    
    Args:
        customer_id (int): Shopify customer ID
        new_tags (list): List of new tags to add
        existing_tags_str (str): Existing tags as comma-separated string
        
    Returns:
        dict: Response with success status
    """
    try:
        url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/customers/{customer_id}.json"
        headers = get_shopify_headers()
        
        # Parse existing tags
        existing_tags = [tag.strip() for tag in existing_tags_str.split(',') if tag.strip()]
        
        # Merge with new tags (avoid duplicates)
        all_tags = list(set(existing_tags + new_tags))
        
        # Update customer
        update_data = {
            'customer': {
                'id': customer_id,
                'tags': ', '.join(all_tags)
            }
        }
        
        response = requests.put(url, headers=headers, json=update_data, timeout=10)
        
        if response.status_code == 200:
            return {
                'success': True,
                'customer_id': customer_id,
                'message': 'Customer tags updated successfully',
                'existing': True
            }
        else:
            return {
                'success': False,
                'error': f'Failed to update customer tags: {response.status_code}',
                'status_code': response.status_code
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Exception updating customer tags: {str(e)}'
        }

def get_customer_by_id(customer_id):
    """
    Retrieve customer details from Shopify by ID
    
    Args:
        customer_id (int): Shopify customer ID
        
    Returns:
        dict: Customer data or None
    """
    try:
        url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/customers/{customer_id}.json"
        headers = get_shopify_headers()
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('customer')
        else:
            print(f"Failed to get customer: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error getting Shopify customer: {e}")
        return None
