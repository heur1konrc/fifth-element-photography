"""
Lumaprints Library Mapping Manager
Tracks which gallery images have been manually uploaded to Lumaprints library
"""

import os
import json
from datetime import datetime

class LumaprintsMapping:
    def __init__(self):
        self.mapping_file = '/data/lumaprints_mapping.json'
    
    def load_mapping(self):
        """Load mapping of gallery images to Lumaprints library IDs"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_mapping(self, mapping):
        """Save mapping of gallery images to Lumaprints library IDs"""
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
    
    def add_mapping(self, filename, library_id, library_name=None):
        """
        Add mapping between gallery image and Lumaprints library ID
        
        Args:
            filename: Gallery image filename
            library_id: Lumaprints library ID (e.g., "IMG_8653_1")
            library_name: Optional descriptive name
            
        Returns:
            (success, message)
        """
        try:
            mapping = self.load_mapping()
            
            # Check if library_id is already used
            for existing_filename, data in mapping.items():
                if data.get('library_id') == library_id and existing_filename != filename:
                    return False, f"Library ID {library_id} is already mapped to {existing_filename}"
            
            mapping[filename] = {
                'library_id': library_id,
                'library_name': library_name,
                'mapped_at': datetime.now().isoformat(),
                'status': 'mapped'
            }
            
            self.save_mapping(mapping)
            return True, f"Successfully mapped {filename} to library ID {library_id}"
            
        except Exception as e:
            return False, str(e)
    
    def remove_mapping(self, filename):
        """
        Remove mapping for a gallery image
        
        Args:
            filename: Gallery image filename
            
        Returns:
            (success, message)
        """
        try:
            mapping = self.load_mapping()
            
            if filename in mapping:
                del mapping[filename]
                self.save_mapping(mapping)
                return True, f"Removed mapping for {filename}"
            else:
                return False, f"No mapping found for {filename}"
                
        except Exception as e:
            return False, str(e)
    
    def get_library_id(self, filename):
        """Get Lumaprints library ID for a gallery image"""
        mapping = self.load_mapping()
        return mapping.get(filename, {}).get('library_id')
    
    def is_mapped(self, filename):
        """Check if an image is mapped to Lumaprints library"""
        mapping = self.load_mapping()
        return filename in mapping and mapping[filename].get('status') == 'mapped'
    
    def get_mapping_status_for_all_images(self):
        """Get mapping status for all gallery images"""
        gallery_images = self.get_gallery_images()
        mapping = self.load_mapping()
        
        status_list = []
        for filename in gallery_images:
            image_data = mapping.get(filename, {})
            
            # Get file size from /data (these ARE the original files)
            file_path = os.path.join('/data', filename)
            file_size_bytes = 0
            file_size_mb = 0
            
            if os.path.exists(file_path):
                file_size_bytes = os.path.getsize(file_path)
                file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
            
            status_list.append({
                'filename': filename,
                'mapped': image_data.get('status') == 'mapped',
                'library_id': image_data.get('library_id'),
                'library_name': image_data.get('library_name'),
                'mapped_at': image_data.get('mapped_at'),
                'file_size_bytes': file_size_bytes,
                'file_size_mb': file_size_mb
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
    
    def get_lumaprints_reference_for_order(self, filename):
        """
        Get the Lumaprints library reference for an order
        
        Args:
            filename: Gallery image filename
            
        Returns:
            Dictionary with library reference or None if not mapped
        """
        library_id = self.get_library_id(filename)
        
        if library_id:
            return {
                'type': 'library',
                'libraryId': library_id
            }
        else:
            return None
    
    def get_mapping_stats(self):
        """Get statistics about mapping status"""
        gallery_images = self.get_gallery_images()
        mapping = self.load_mapping()
        
        total_images = len(gallery_images)
        mapped_images = len([f for f in gallery_images if f in mapping and mapping[f].get('status') == 'mapped'])
        unmapped_images = total_images - mapped_images
        mapping_percentage = (mapped_images / total_images * 100) if total_images > 0 else 0
        
        return {
            'total_images': total_images,
            'mapped_images': mapped_images,
            'unmapped_images': unmapped_images,
            'mapping_percentage': round(mapping_percentage, 1)
        }
    
    def export_mapping_data(self):
        """Export mapping data as JSON"""
        mapping = self.load_mapping()
        stats = self.get_mapping_stats()
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'stats': stats,
            'mappings': mapping
        }
        
        return export_data
    
    def validate_mapping(self, filename, library_id):
        """
        Validate that a mapping is correct
        Note: This would ideally check with Lumaprints API if the library ID exists,
        but since their API doesn't have library endpoints, we just do basic validation
        """
        if not filename or not library_id:
            return False, "Filename and Library ID are required"
        
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return False, "Invalid image file format"
        
        # Basic library ID format validation (adjust based on Lumaprints format)
        if len(library_id.strip()) < 3:
            return False, "Library ID seems too short"
        
        return True, "Mapping appears valid"
