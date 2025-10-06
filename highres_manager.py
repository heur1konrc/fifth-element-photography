"""
High-Resolution Image Manager for Lumaprints Integration
Provides secure access to high-res images for print orders
"""

import os
import json
import uuid
import hashlib
import time
from datetime import datetime, timedelta
from flask import send_from_directory, abort, request

class HighResManager:
    def __init__(self, app):
        self.app = app
        self.highres_dir = '/data/highres'
        self.mapping_file = '/data/highres_mapping.json'
        self.tokens_file = '/data/access_tokens.json'
        
        # Ensure directories exist
        os.makedirs(self.highres_dir, exist_ok=True)
        
        # Register routes
        self.register_routes()
    
    def register_routes(self):
        """Register Flask routes for high-res image management"""
        
        @self.app.route('/admin/highres')
        def admin_highres():
            """Admin interface for managing high-res images"""
            gallery_images = self.get_gallery_images()
            highres_mapping = self.load_mapping()
            return self.app.render_template('admin_highres.html', 
                                          gallery_images=gallery_images,
                                          highres_mapping=highres_mapping)
        
        @self.app.route('/api/highres/upload', methods=['POST'])
        def upload_highres():
            """Upload high-res version of an image"""
            if 'file' not in request.files:
                return {'success': False, 'error': 'No file provided'}, 400
            
            file = request.files['file']
            gallery_filename = request.form.get('gallery_filename')
            
            if not gallery_filename:
                return {'success': False, 'error': 'Gallery filename required'}, 400
            
            if file.filename == '':
                return {'success': False, 'error': 'No file selected'}, 400
            
            # Save high-res file
            highres_filename = f"hr_{gallery_filename}"
            filepath = os.path.join(self.highres_dir, highres_filename)
            file.save(filepath)
            
            # Update mapping
            self.update_mapping(gallery_filename, highres_filename)
            
            return {'success': True, 'message': 'High-res image uploaded successfully'}
        
        @self.app.route('/api/highres/mapping')
        def get_mapping():
            """Get the current gallery to high-res mapping"""
            return self.load_mapping()
        
        @self.app.route('/secure/highres/<token>/<filename>')
        def serve_highres_secure(token, filename):
            """Serve high-res images with secure token authentication"""
            if not self.validate_token(token):
                abort(403)
            
            filepath = os.path.join(self.highres_dir, filename)
            if not os.path.exists(filepath):
                abort(404)
            
            return send_from_directory(self.highres_dir, filename)
    
    def get_gallery_images(self):
        """Get list of gallery images from /data directory"""
        images = []
        data_dir = '/data'
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    images.append(filename)
        
        return sorted(images)
    
    def load_mapping(self):
        """Load gallery to high-res filename mapping"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def update_mapping(self, gallery_filename, highres_filename):
        """Update the mapping between gallery and high-res images"""
        mapping = self.load_mapping()
        mapping[gallery_filename] = {
            'highres_filename': highres_filename,
            'uploaded_at': datetime.now().isoformat(),
            'file_size': os.path.getsize(os.path.join(self.highres_dir, highres_filename))
        }
        
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
    
    def generate_secure_token(self, filename, duration_hours=24):
        """Generate a secure token for accessing high-res images"""
        token_data = {
            'filename': filename,
            'expires': (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            'created': datetime.now().isoformat()
        }
        
        # Create unique token
        token = str(uuid.uuid4())
        
        # Save token
        tokens = self.load_tokens()
        tokens[token] = token_data
        self.save_tokens(tokens)
        
        return token
    
    def validate_token(self, token):
        """Validate a secure access token"""
        tokens = self.load_tokens()
        
        if token not in tokens:
            return False
        
        token_data = tokens[token]
        expires = datetime.fromisoformat(token_data['expires'])
        
        if datetime.now() > expires:
            # Token expired, remove it
            del tokens[token]
            self.save_tokens(tokens)
            return False
        
        return True
    
    def load_tokens(self):
        """Load access tokens"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_tokens(self, tokens):
        """Save access tokens"""
        with open(self.tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def get_highres_url_for_lumaprints(self, gallery_filename):
        """Get secure URL for high-res image for Lumaprints API"""
        mapping = self.load_mapping()
        
        if gallery_filename not in mapping:
            return None
        
        highres_filename = mapping[gallery_filename]['highres_filename']
        token = self.generate_secure_token(highres_filename, duration_hours=48)
        
        # Return full URL that Lumaprints can access
        base_url = "https://fifth-element-photography-production.up.railway.app"
        return f"{base_url}/secure/highres/{token}/{highres_filename}"
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens (call this periodically)"""
        tokens = self.load_tokens()
        current_time = datetime.now()
        
        expired_tokens = []
        for token, data in tokens.items():
            expires = datetime.fromisoformat(data['expires'])
            if current_time > expires:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del tokens[token]
        
        if expired_tokens:
            self.save_tokens(tokens)
        
        return len(expired_tokens)
