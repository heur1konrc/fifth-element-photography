"""
Lumaprints Library Manager
Handles uploading images to Lumaprints library and tracking sync status
"""

import os
import json
import requests
import base64
from datetime import datetime
from lumaprints_api import get_lumaprints_client

class LumaprintsLibrary:
    def __init__(self):
        self.library_mapping_file = '/data/lumaprints_library_mapping.json'
        self.api_client = get_lumaprints_client(sandbox=True)
    
    def load_library_mapping(self):
        """Load mapping of gallery images to Lumaprints library IDs"""
        try:
            if os.path.exists(self.library_mapping_file):
                with open(self.library_mapping_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_library_mapping(self, mapping):
        """Save mapping of gallery images to Lumaprints library IDs"""
        with open(self.library_mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
    
    def upload_image_to_lumaprints(self, image_path, filename):
        """
        Upload an image to Lumaprints library
        Returns: (success, library_id_or_error)
        """
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Encode image as base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare upload payload
            upload_payload = {
                "fileName": filename,
                "fileData": image_base64,
                "description": f"Gallery image: {filename}",
                "tags": ["gallery", "fifth-element-photography"]
            }
            
            # Upload to Lumaprints library
            response = self.api_client.upload_to_library(upload_payload)
            
            if response.get('success'):
                library_id = response.get('libraryId')
                
                # Update mapping
                mapping = self.load_library_mapping()
                mapping[filename] = {
                    'library_id': library_id,
                    'uploaded_at': datetime.now().isoformat(),
                    'status': 'synced',
                    'file_size': len(image_data)
                }
                self.save_library_mapping(mapping)
                
                return True, library_id
            else:
                return False, response.get('error', 'Unknown error')
                
        except Exception as e:
            return False, str(e)
    
    def check_sync_status(self, filename):
        """Check if an image is synced with Lumaprints library"""
        mapping = self.load_library_mapping()
        return mapping.get(filename, {}).get('status') == 'synced'
    
    def get_library_id(self, filename):
        """Get Lumaprints library ID for a gallery image"""
        mapping = self.load_library_mapping()
        return mapping.get(filename, {}).get('library_id')
    
    def get_sync_status_for_all_images(self):
        """Get sync status for all gallery images"""
        gallery_images = self.get_gallery_images()
        mapping = self.load_library_mapping()
        
        status_list = []
        for filename in gallery_images:
            image_data = mapping.get(filename, {})
            status_list.append({
                'filename': filename,
                'synced': image_data.get('status') == 'synced',
                'library_id': image_data.get('library_id'),
                'uploaded_at': image_data.get('uploaded_at'),
                'file_size': image_data.get('file_size')
            })
        
        return status_list
    
    def get_gallery_images(self):
        """Get list of all gallery images"""
        images = []
        data_dir = '/data'
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    images.append(filename)
        
        return sorted(images)
    
    def bulk_upload_missing_images(self):
        """Upload all gallery images that aren't synced to Lumaprints"""
        gallery_images = self.get_gallery_images()
        mapping = self.load_library_mapping()
        
        results = []
        for filename in gallery_images:
            if filename not in mapping or mapping[filename].get('status') != 'synced':
                image_path = os.path.join('/data', filename)
                success, result = self.upload_image_to_lumaprints(image_path, filename)
                
                results.append({
                    'filename': filename,
                    'success': success,
                    'result': result
                })
        
        return results
    
    def remove_from_library(self, filename):
        """Remove image from Lumaprints library and update mapping"""
        mapping = self.load_library_mapping()
        
        if filename in mapping:
            library_id = mapping[filename].get('library_id')
            
            # Try to delete from Lumaprints (if API supports it)
            try:
                # Note: Check if Lumaprints API has delete endpoint
                # self.api_client.delete_from_library(library_id)
                pass
            except:
                pass
            
            # Remove from local mapping
            del mapping[filename]
            self.save_library_mapping(mapping)
            
            return True
        
        return False
    
    def get_lumaprints_url_for_order(self, filename):
        """Get the Lumaprints library reference for an order"""
        library_id = self.get_library_id(filename)
        
        if library_id:
            return {
                'type': 'library',
                'libraryId': library_id
            }
        else:
            # Image not in library - need to upload first
            return None
