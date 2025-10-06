"""
Image Storage Manager
Handles both web-optimized and high-resolution image storage
"""

import os
import json
from PIL import Image
from datetime import datetime

class ImageStorageManager:
    def __init__(self):
        self.web_images_dir = '/data'  # Web-optimized images for gallery
        self.highres_images_dir = '/data/originals'  # Original high-res images
        self.storage_info_file = '/data/image_storage_info.json'
        
        # Ensure directories exist
        os.makedirs(self.web_images_dir, exist_ok=True)
        os.makedirs(self.highres_images_dir, exist_ok=True)
    
    def load_storage_info(self):
        """Load storage information for all images"""
        try:
            if os.path.exists(self.storage_info_file):
                with open(self.storage_info_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_storage_info(self, storage_info):
        """Save storage information"""
        with open(self.storage_info_file, 'w') as f:
            json.dump(storage_info, f, indent=2)
    
    def store_image_dual(self, uploaded_file, filename):
        """
        Store image in both web-optimized and high-res versions
        
        Args:
            uploaded_file: Flask uploaded file object
            filename: Secure filename to use
            
        Returns:
            (success, message, file_info)
        """
        try:
            # Save original high-res version
            highres_path = os.path.join(self.highres_images_dir, filename)
            uploaded_file.save(highres_path)
            
            # Get original file info
            original_size = os.path.getsize(highres_path)
            
            # Create web-optimized version
            web_path = os.path.join(self.web_images_dir, filename)
            
            with Image.open(highres_path) as img:
                # Get original dimensions
                original_width, original_height = img.size
                
                # Create web version (max 1920px width, 85% quality)
                web_img = img.copy()
                
                # Resize if too large
                max_width = 1920
                if original_width > max_width:
                    ratio = max_width / original_width
                    new_height = int(original_height * ratio)
                    web_img = web_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Save web version with compression
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    web_img.save(web_path, 'JPEG', quality=85, optimize=True)
                else:
                    web_img.save(web_path, optimize=True)
            
            # Get web file info
            web_size = os.path.getsize(web_path)
            
            # Store information
            storage_info = self.load_storage_info()
            storage_info[filename] = {
                'original_size_bytes': original_size,
                'original_size_mb': round(original_size / (1024 * 1024), 2),
                'web_size_bytes': web_size,
                'web_size_mb': round(web_size / (1024 * 1024), 2),
                'original_dimensions': f"{original_width}x{original_height}",
                'web_dimensions': f"{web_img.width}x{web_img.height}",
                'uploaded_at': datetime.now().isoformat(),
                'has_highres': True
            }
            self.save_storage_info(storage_info)
            
            return True, f"Successfully stored {filename} (Original: {storage_info[filename]['original_size_mb']}MB, Web: {storage_info[filename]['web_size_mb']}MB)", storage_info[filename]
            
        except Exception as e:
            return False, f"Error storing image: {str(e)}", None
    
    def get_highres_path(self, filename):
        """Get path to high-res version of image"""
        highres_path = os.path.join(self.highres_images_dir, filename)
        if os.path.exists(highres_path):
            return highres_path
        return None
    
    def get_web_path(self, filename):
        """Get path to web version of image"""
        web_path = os.path.join(self.web_images_dir, filename)
        if os.path.exists(web_path):
            return web_path
        return None
    
    def has_highres_version(self, filename):
        """Check if high-res version exists for an image"""
        return self.get_highres_path(filename) is not None
    
    def get_image_info(self, filename):
        """Get storage information for an image"""
        storage_info = self.load_storage_info()
        return storage_info.get(filename, {})
    
    def get_all_images_info(self):
        """Get storage information for all images"""
        storage_info = self.load_storage_info()
        
        # Also check for images that might not be in storage_info yet
        web_images = []
        if os.path.exists(self.web_images_dir):
            for filename in os.listdir(self.web_images_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    web_images.append(filename)
        
        # Merge with storage info
        all_info = {}
        for filename in web_images:
            if filename in storage_info:
                all_info[filename] = storage_info[filename]
            else:
                # Generate info for legacy images
                web_path = os.path.join(self.web_images_dir, filename)
                highres_path = os.path.join(self.highres_images_dir, filename)
                
                web_size = os.path.getsize(web_path) if os.path.exists(web_path) else 0
                highres_size = os.path.getsize(highres_path) if os.path.exists(highres_path) else 0
                
                all_info[filename] = {
                    'original_size_bytes': highres_size if highres_size > 0 else web_size,
                    'original_size_mb': round((highres_size if highres_size > 0 else web_size) / (1024 * 1024), 2),
                    'web_size_bytes': web_size,
                    'web_size_mb': round(web_size / (1024 * 1024), 2),
                    'has_highres': os.path.exists(highres_path),
                    'uploaded_at': 'Unknown'
                }
        
        return all_info
    
    def migrate_existing_images(self):
        """Migrate existing images to dual storage system"""
        migrated = []
        
        if os.path.exists(self.web_images_dir):
            for filename in os.listdir(self.web_images_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    web_path = os.path.join(self.web_images_dir, filename)
                    highres_path = os.path.join(self.highres_images_dir, filename)
                    
                    # If high-res doesn't exist, copy web version as high-res
                    if not os.path.exists(highres_path):
                        import shutil
                        shutil.copy2(web_path, highres_path)
                        migrated.append(filename)
        
        return migrated
