"""
Lumaprints API Integration for Fifth Element Photography
Core functions for connecting to Lumaprints API and handling print orders
"""

import requests
import base64
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class LumaprintsAPI:
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = True):
        """
        Initialize Lumaprints API client
        
        Args:
            api_key: Your Lumaprints API key
            api_secret: Your Lumaprints API secret
            sandbox: Use sandbox environment (True) or production (False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        
        # Set base URL based on environment
        if sandbox:
            self.base_url = "https://us.api-sandbox.lumaprints.com/api/v1"
        else:
            self.base_url = "https://us.api.lumaprints.com/api/v1"
        
        # Create authentication header
        credentials = f"{api_key}:{api_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        # Store credentials for reference
        self.api_key_preview = f"{api_key[:20]}..."
        self.api_secret_preview = f"{api_secret[:20]}..."
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 30) -> Dict:
        """
        Make authenticated request to Lumaprints API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request payload for POST requests
            timeout: Request timeout in seconds (default 30)
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # For check_image endpoint, return response even on 400/406 errors
            # These contain valuable error details from Lumaprints
            if response.status_code in [200, 400, 406]:
                try:
                    result = response.json()
                    # Add status code to result for error handling (only for dict responses)
                    if isinstance(result, dict):
                        result['_status_code'] = response.status_code
                    return result
                except ValueError:
                    # Response is not JSON
                    return {
                        '_status_code': response.status_code,
                        'message': response.text
                    }
            
            # For other status codes, raise an error
            response.raise_for_status()
            
            # Return JSON response for successful requests
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
    
    def get_categories(self) -> List[Dict]:
        """
        Get all available product categories
        
        Returns:
            List of category dictionaries
        """
        return self._make_request("GET", "/products/categories")
    
    def get_subcategories(self, category_id: int) -> List[Dict]:
        """
        Get subcategories for a specific category
        
        Args:
            category_id: ID of the parent category
            
        Returns:
            List of subcategory dictionaries
        """
        return self._make_request("GET", f"/products/categories/{category_id}/subcategories")
    
    def get_subcategory_options(self, subcategory_id: int) -> List[Dict]:
        """
        Get all available options for a subcategory
        
        Args:
            subcategory_id: ID of the subcategory
            
        Returns:
            List of option dictionaries
        """
        return self._make_request("GET", f"/products/subcategories/{subcategory_id}/options")
    
    def get_stores(self) -> List[Dict]:
        """
        Get all available stores for API order creation
        
        Returns:
            List of store dictionaries
        """
        return self._make_request("GET", "/stores")
    
    def check_image(self, subcategory_id: int, print_width: float, print_height: float, 
                   image_url: str, order_item_options: List[int] = None) -> Dict:
        """
        Check if an image meets quality requirements for printing
        
        Args:
            subcategory_id: ID of the subcategory
            print_width: Print width in inches
            print_height: Print height in inches
            image_url: URL of the image to check
            order_item_options: List of option IDs for the product
            
        Returns:
            Image check result dictionary
        """
        data = {
            "subcategoryId": subcategory_id,
            "printWidth": print_width,
            "printHeight": print_height,
            "imageUrl": image_url,
            "orderItemOptions": order_item_options or []
        }
        
        # Use longer timeout for image checking (can take time to download and validate)
        return self._make_request("POST", "/images/checkImageConfig", data, timeout=60)
    
    def submit_order(self, order_data: Dict) -> Dict:
        """
        Submit an order to Lumaprints
        
        Args:
            order_data: Complete order payload dictionary
            
        Returns:
            Order submission result dictionary
        """
        return self._make_request("POST", "/orders", order_data)
    
    def get_order(self, order_id: str) -> Dict:
        """
        Get order details by order ID
        
        Args:
            order_id: Lumaprints order ID
            
        Returns:
            Order details dictionary
        """
        return self._make_request("GET", f"/orders/{order_id}")
    
    def get_pricing(self, subcategory_id: int, width: float, height: float, 
                   quantity: int = 1, options: Optional[List[int]] = None) -> Dict:
        """
        Get pricing for a specific product configuration
        
        Args:
            subcategory_id: Product subcategory ID
            width: Print width in inches
            height: Print height in inches
            quantity: Number of prints
            options: List of option IDs for customization
            
        Returns:
            Pricing information dictionary
        """
        data = {
            "subcategoryId": subcategory_id,
            "width": width,
            "height": height,
            "quantity": quantity
        }
        
        if options:
            data["options"] = options
            
        return self._make_request("POST", "/pricing", data)
    
    def submit_order(self, order_data: Dict) -> Dict:
        """
        Submit an order to Lumaprints for fulfillment
        
        Args:
            order_data: Complete order information dictionary
            
        Returns:
            Order submission result
        """
        return self._make_request("POST", "/orders", order_data)
    
    def get_order(self, order_number: int) -> Dict:
        """
        Get details of a specific order
        
        Args:
            order_number: Lumaprints order number
            
        Returns:
            Order details dictionary
        """
        return self._make_request("GET", f"/orders/{order_number}")
    
    def get_order_shipments(self, order_number: int) -> List[Dict]:
        """
        Get shipment information for an order
        
        Args:
            order_number: Lumaprints order number
            
        Returns:
            List of shipment dictionaries
        """
        return self._make_request("GET", f"/orders/{order_number}/shipments")


class LumaprintsPricingCalculator:
    """
    Helper class for calculating retail prices with markup
    """
    
    def __init__(self, api_client: LumaprintsAPI, markup_percentage: float = 100.0):
        """
        Initialize pricing calculator
        
        Args:
            api_client: Lumaprints API client instance
            markup_percentage: Markup percentage (100.0 = 100% markup, doubling the price)
        """
        self.api = api_client
        self.markup_percentage = markup_percentage
    
    def calculate_retail_price(self, subcategory_id: int, width: float, height: float, 
                             quantity: int = 1, options: Optional[List[int]] = None) -> Dict:
        """
        Calculate retail price with markup
        
        Args:
            subcategory_id: Product subcategory ID
            width: Print width in inches
            height: Print height in inches
            quantity: Number of prints
            options: List of option IDs
            
        Returns:
            Dictionary with wholesale price, markup, and retail price
        """
        try:
            # Get wholesale pricing from Lumaprints
            pricing_response = self.api.get_pricing(subcategory_id, width, height, quantity, options)
            
            # Extract wholesale price (this may vary based on API response structure)
            wholesale_price = pricing_response.get('price', 0.0)
            
            # Calculate markup and retail price
            markup_amount = wholesale_price * (self.markup_percentage / 100.0)
            retail_price = wholesale_price + markup_amount
            
            return {
                'wholesale_price': wholesale_price,
                'markup_percentage': self.markup_percentage,
                'markup_amount': markup_amount,
                'retail_price': retail_price,
                'quantity': quantity,
                'price_per_item': retail_price / quantity if quantity > 0 else 0,
                'raw_response': pricing_response
            }
            
        except Exception as e:
            print(f"Error calculating retail price: {e}")
            return {
                'error': str(e),
                'wholesale_price': 0.0,
                'retail_price': 0.0
            }


# Initialize API client with your credentials
def get_lumaprints_client(sandbox: bool = True) -> LumaprintsAPI:
    """
    Get configured Lumaprints API client
    
    Args:
        sandbox: Use sandbox environment
        
    Returns:
        Configured API client
    """
    # Load credentials from environment or use defaults
    import os
    API_KEY = os.getenv('LUMAPRINTS_API_KEY', 'e909ca3adc5026beb5dc306020ffe3068cf0e5962d31303137373136')
    API_SECRET = os.getenv('LUMAPRINTS_API_SECRET', '23ab680f283aeabd077e2d31303137373136')
    
    return LumaprintsAPI(API_KEY, API_SECRET, sandbox=sandbox)


# Initialize pricing calculator with 100% markup (double the wholesale price)
def get_pricing_calculator(markup_percentage: float = 100.0, sandbox: bool = True) -> LumaprintsPricingCalculator:
    """
    Get configured pricing calculator
    
    Args:
        markup_percentage: Markup percentage (100.0 = 100% markup)
        sandbox: Use sandbox environment
        
    Returns:
        Configured pricing calculator
    """
    api_client = get_lumaprints_client(sandbox=sandbox)
    return LumaprintsPricingCalculator(api_client, markup_percentage)


# Test function to verify API connection
def test_api_connection():
    """
    Test the API connection and print basic information
    """
    try:
        print("Testing Lumaprints API connection...")
        
        # Initialize API client
        api = get_lumaprints_client(sandbox=True)
        
        # Test getting categories
        print("Fetching categories...")
        categories = api.get_categories()
        print(f"Found {len(categories)} categories:")
        for cat in categories[:3]:  # Show first 3 categories
            print(f"  - {cat.get('name', 'Unknown')} (ID: {cat.get('id', 'Unknown')})")
        
        # Test getting stores
        print("\nFetching stores...")
        stores = api.get_stores()
        print(f"Found {len(stores)} stores:")
        for store in stores[:2]:  # Show first 2 stores
            print(f"  - {store.get('name', 'Unknown')} (ID: {store.get('id', 'Unknown')})")
        
        print("\n✅ API connection successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Run test when script is executed directly
    test_api_connection()

    
    def upload_to_library(self, upload_data: Dict) -> Dict:
        """
        Upload an image to Lumaprints library
        
        Args:
            upload_data: Dictionary containing:
                - fileName: Name of the file
                - fileData: Base64 encoded image data
                - description: Optional description
                - tags: Optional list of tags
                
        Returns:
            Upload result dictionary with libraryId if successful
        """
        return self._make_request("POST", "/library/upload", upload_data)
    
    def get_library_images(self) -> List[Dict]:
        """
        Get all images from Lumaprints library
        
        Returns:
            List of library image dictionaries
        """
        return self._make_request("GET", "/library/images")
    
    def delete_from_library(self, library_id: str) -> Dict:
        """
        Delete an image from Lumaprints library
        
        Args:
            library_id: ID of the library image to delete
            
        Returns:
            Deletion result dictionary
        """
        return self._make_request("DELETE", f"/library/images/{library_id}")
