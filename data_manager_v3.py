"""
Data Manager V3 - Fifth Element Photography
Version: 3.0.1

This module provides a clean interface for all data persistence operations.
It handles reading from and writing to JSON data files, isolating the
application logic from the specifics of data storage.

All data operations go through this module to ensure consistency and
make future data storage changes easier.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from PIL import Image


class DataManagerV3:
    """
    Manages all data persistence for Admin V3.
    
    Handles:
    - Image metadata (titles, descriptions)
    - Category assignments (multi-category support)
    - Category management
    - Featured/hero image selection
    """
    
    def __init__(self, data_dir: str = "/data"):
        """
        Initialize the data manager.
        
        Args:
            data_dir: Path to the data directory (default: /data for Railway)
        """
        self.data_dir = Path(data_dir)
        # Images are stored directly in /data/, not in a subdirectory
        self.images_dir = self.data_dir
        # Thumbnails stored in /data/thumbnails/
        self.thumbnails_dir = self.data_dir / "thumbnails"
        
        # Data file paths - V3 uses separate files to avoid conflicts with old system
        self.metadata_file = self.data_dir / "image_metadata_v3.json"
        self.categories_file = self.data_dir / "image_categories_v3.json"
        self.category_list_file = self.data_dir / "categories_v3.json"
        self.featured_file = self.data_dir / "featured_image_v3.json"
        self.hero_file = self.data_dir / "hero_image_v3.json"
        
        # Ensure directories exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Create empty data files if they don't exist."""
        if not self.metadata_file.exists():
            self._write_json(self.metadata_file, {})
        
        if not self.categories_file.exists():
            self._write_json(self.categories_file, {})
        
        if not self.category_list_file.exists():
            self._write_json(self.category_list_file, [])
        
        if not self.featured_file.exists():
            self._write_json(self.featured_file, {"filename": None})
        
        if not self.hero_file.exists():
            self._write_json(self.hero_file, {"filename": None})
    
    def _read_json(self, filepath: Path) -> Any:
        """
        Read and parse a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if filepath.name != "categories.json" else []
    
    def _write_json(self, filepath: Path, data: Any):
        """
        Write data to a JSON file.
        
        Args:
            filepath: Path to the JSON file
            data: Data to write
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== IMAGE OPERATIONS ====================
    
    def get_all_images(self) -> List[Dict[str, Any]]:
        """
        Get all images with their metadata and categories.
        
        Returns:
            List of image dictionaries with filename, title, description, categories
        """
        metadata = self._read_json(self.metadata_file)
        categories = self._read_json(self.categories_file)
        
        images = []
        for filename in self.images_dir.iterdir():
            if filename.is_file() and filename.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                image_data = {
                    'filename': filename.name,
                    'title': metadata.get(filename.name, {}).get('title', filename.stem),
                    'description': metadata.get(filename.name, {}).get('description', ''),
                    'categories': categories.get(filename.name, []),
                    'featured': metadata.get(filename.name, {}).get('featured', False),
                    'is_hero': metadata.get(filename.name, {}).get('is_hero', False),
                    'upload_date': datetime.fromtimestamp(filename.stat().st_mtime).isoformat()
                }
                images.append(image_data)
        
        return images
    
    def get_image(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get a single image's data.
        
        Args:
            filename: Image filename
            
        Returns:
            Image dictionary or None if not found
        """
        image_path = self.images_dir / filename
        if not image_path.exists():
            return None
        
        metadata = self._read_json(self.metadata_file)
        categories = self._read_json(self.categories_file)
        
        return {
            'filename': filename,
            'title': metadata.get(filename, {}).get('title', Path(filename).stem),
            'description': metadata.get(filename, {}).get('description', ''),
            'categories': categories.get(filename, []),
            'featured': metadata.get(filename, {}).get('featured', False),
            'is_hero': metadata.get(filename, {}).get('is_hero', False),
            'order_prints_enabled': metadata.get(filename, {}).get('order_prints_enabled', False),
            'shopify_product_handle': metadata.get(filename, {}).get('shopify_product_handle', '')
        }
    
    def update_image_metadata(self, filename: str, title: Optional[str] = None, 
                             description: Optional[str] = None, featured: Optional[bool] = None,
                             order_prints_enabled: Optional[bool] = None,
                             shopify_product_handle: Optional[str] = None) -> bool:
        """
        Update an image's title and/or description.
        
        Args:
            filename: Image filename
            title: New title (optional)
            description: New description (optional)
            featured: Featured flag (optional)
            order_prints_enabled: Enable/disable order prints (optional)
            
        Returns:
            True if successful, False otherwise
        """
        metadata = self._read_json(self.metadata_file)
        
        if filename not in metadata:
            metadata[filename] = {}
        
        if title is not None:
            metadata[filename]['title'] = title
        
        if description is not None:
            metadata[filename]['description'] = description
        
        if featured is not None:
            metadata[filename]['featured'] = featured
        
        if order_prints_enabled is not None:
            metadata[filename]['order_prints_enabled'] = order_prints_enabled
        
        if shopify_product_handle is not None:
            metadata[filename]['shopify_product_handle'] = shopify_product_handle
        
        self._write_json(self.metadata_file, metadata)
        return True
    
    def update_image_categories(self, filename: str, categories: List[str]) -> bool:
        """
        Update an image's category assignments.
        
        Args:
            filename: Image filename
            categories: List of category names
            
        Returns:
            True if successful, False otherwise
        """
        category_data = self._read_json(self.categories_file)
        category_data[filename] = categories
        self._write_json(self.categories_file, category_data)
        return True
    
    def assign_categories(self, filenames: List[str], categories: List[str]) -> int:
        """
        Assign categories to multiple images at once.
        
        Args:
            filenames: List of image filenames
            categories: List of category names to assign
            
        Returns:
            Number of images successfully updated
        """
        category_data = self._read_json(self.categories_file)
        success_count = 0
        
        for filename in filenames:
            # Get existing categories for this image
            existing = category_data.get(filename, [])
            # Add new categories (avoid duplicates)
            updated = list(set(existing + categories))
            category_data[filename] = updated
            success_count += 1
        
        self._write_json(self.categories_file, category_data)
        return success_count
    
    def delete_image(self, filename: str) -> bool:
        """
        Delete an image and all its associated data.
        
        Args:
            filename: Image filename
            
        Returns:
            True if successful, False otherwise
        """
        image_path = self.images_dir / filename
        if not image_path.exists():
            return False
        
        # Delete the image file
        image_path.unlink()
        
        # Remove from metadata
        metadata = self._read_json(self.metadata_file)
        if filename in metadata:
            del metadata[filename]
            self._write_json(self.metadata_file, metadata)
        
        # Remove from categories
        categories = self._read_json(self.categories_file)
        if filename in categories:
            del categories[filename]
            self._write_json(self.categories_file, categories)
        
        return True
    
    # ==================== CATEGORY OPERATIONS ====================
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories with image counts.
        
        Returns:
            List of category dictionaries with name and count
        """
        category_list = self._read_json(self.category_list_file)
        category_assignments = self._read_json(self.categories_file)
        
        # Count images per category
        category_counts = {}
        for filename, cats in category_assignments.items():
            for cat in cats:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return [
            {
                'name': cat,
                'count': category_counts.get(cat, 0)
            }
            for cat in category_list
        ]
    
    def create_category(self, category_name: str) -> bool:
        """
        Create a new category.
        
        Args:
            category_name: Name of the new category
            
        Returns:
            True if successful, False if category already exists
        """
        categories = self._read_json(self.category_list_file)
        
        if category_name in categories:
            return False
        
        categories.append(category_name)
        self._write_json(self.category_list_file, categories)
        return True
    
    def delete_category(self, category_name: str) -> bool:
        """
        Delete a category and remove it from all images.
        
        Args:
            category_name: Name of the category to delete
            
        Returns:
            True if successful, False if category doesn't exist
        """
        categories = self._read_json(self.category_list_file)
        
        if category_name not in categories:
            return False
        
        # Remove from category list
        categories.remove(category_name)
        self._write_json(self.category_list_file, categories)
        
        # Remove from all image assignments
        category_assignments = self._read_json(self.categories_file)
        for filename in category_assignments:
            if category_name in category_assignments[filename]:
                category_assignments[filename].remove(category_name)
        
        self._write_json(self.categories_file, category_assignments)
        return True
    
    # ==================== FEATURED/HERO OPERATIONS ====================
    
    def set_featured_image(self, filename: str) -> bool:
        """Set the featured image."""
        self._write_json(self.featured_file, {"filename": filename})
        return True
    
    def get_featured_image(self) -> Optional[str]:
        """Get the featured image filename."""
        data = self._read_json(self.featured_file)
        return data.get("filename")
    
    def set_hero_image(self, filename: str) -> bool:
        """Set the hero image."""
        self._write_json(self.hero_file, {"filename": filename})
        return True
    
    def get_hero_image(self) -> Optional[str]:
        """Get the hero image filename."""
        data = self._read_json(self.hero_file)
        return data.get("filename")
    
    # ==================== THUMBNAIL OPERATIONS ====================
    
    def generate_thumbnail(self, filename: str, max_width: int = 800) -> bool:
        """
        Generate a thumbnail for an image.
        
        Args:
            filename: Name of the image file
            max_width: Maximum width of thumbnail (default: 800px)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            image_path = self.images_dir / filename
            thumbnail_path = self.thumbnails_dir / filename
            
            # Delete existing thumbnail to force regeneration at new quality
            if thumbnail_path.exists():
                thumbnail_path.unlink()
            
            # Open and resize image
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                
                # Calculate new dimensions maintaining aspect ratio
                width, height = img.size
                if width > max_width:
                    new_width = max_width
                    new_height = int((max_width / width) * height)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                img.save(thumbnail_path, 'JPEG', quality=95, optimize=True)
            
            return True
        except Exception as e:
            print(f"Error generating thumbnail for {filename}: {e}")
            return False
    
    def get_thumbnail_path(self, filename: str) -> Path:
        """
        Get the path to a thumbnail, generating it if it doesn't exist.
        
        Args:
            filename: Name of the image file
            
        Returns:
            Path to the thumbnail file
        """
        thumbnail_path = self.thumbnails_dir / filename
        
        # Generate thumbnail if it doesn't exist
        if not thumbnail_path.exists():
            self.generate_thumbnail(filename)
        
        return thumbnail_path
    
    # ==================== EXIF OPERATIONS ====================
    
    def get_exif_data(self, filename: str) -> Dict[str, Any]:
        """
        Extract EXIF data from an image (using same method as production).
        
        Args:
            filename: Name of the image file
            
        Returns:
            Dictionary of EXIF data with human-readable keys
        """
        try:
            from PIL.ExifTags import TAGS
            
            image_path = self.images_dir / filename
            if not image_path.exists():
                return self._get_default_exif()
            
            logging.info(f"Extracting EXIF from: {image_path}")
            
            # Open image and get EXIF data using _getexif() (same as production)
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                img_size = img.size  # Get actual pixel dimensions
            
            if not exif_data:
                logging.info("No EXIF data found in image")
                return self._get_default_exif()
            
            # Convert EXIF data to readable format
            exif = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif[tag] = value
            
            logging.info(f"Found EXIF tags: {list(exif.keys())[:20]}")
            
            # Return formatted EXIF data matching template expectations
            return {
                'camera': self._get_camera_info(exif),
                'lens': self._get_lens_info(exif),
                'aperture': self._get_aperture_info(exif),
                'shutter_speed': self._get_shutter_speed_info(exif),
                'iso': self._get_iso_info(exif),
                'focal_length': self._get_focal_length_info(exif),
                'date_taken': self._get_date_taken(exif),
                'dimensions': self._get_dimensions(exif, img_size)
            }
        
        except Exception as e:
            logging.error(f"Error extracting EXIF from {filename}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return self._get_default_exif()
    
    def _get_camera_info(self, exif: Dict) -> str:
        """Extract camera information from EXIF"""
        make = exif.get('Make', '').strip()
        model = exif.get('Model', '').strip()
        
        if make and model:
            # Remove make from model if it's already included
            if make.lower() in model.lower():
                return model
            else:
                return f"{make} {model}"
        elif model:
            return model
        elif make:
            return make
        else:
            return 'Unavailable'
    
    def _get_lens_info(self, exif: Dict) -> str:
        """Extract lens information from EXIF"""
        # Try different lens fields
        lens_fields = ['LensModel', 'Lens', 'LensInfo', 'LensMake']
        
        for field in lens_fields:
            lens = exif.get(field)
            if lens:
                if isinstance(lens, str):
                    return lens.strip()
                elif isinstance(lens, bytes):
                    try:
                        return lens.decode('utf-8').strip()
                    except:
                        continue
        
        return 'Unavailable'
    
    def _get_aperture_info(self, exif: Dict) -> str:
        """Extract aperture information from EXIF"""
        # Try FNumber first, then ApertureValue
        f_number = exif.get('FNumber')
        if f_number:
            try:
                if isinstance(f_number, tuple) and len(f_number) == 2:
                    aperture = f_number[0] / f_number[1]
                    return f"f/{aperture:.1f}"
                else:
                    # Handle direct float/string values
                    aperture = float(f_number)
                    return f"f/{aperture:.1f}"
            except:
                pass
        
        # Try ApertureValue as backup
        aperture_value = exif.get('ApertureValue')
        if aperture_value:
            try:
                aperture = float(aperture_value)
                return f"f/{aperture:.1f}"
            except:
                pass
        
        return 'Unavailable'
    
    def _get_shutter_speed_info(self, exif: Dict) -> str:
        """Extract shutter speed information from EXIF"""
        exposure_time = exif.get('ExposureTime')
        if exposure_time:
            if isinstance(exposure_time, tuple) and len(exposure_time) == 2:
                if exposure_time[0] == 1:
                    return f"1/{exposure_time[1]}s"
                else:
                    speed = exposure_time[0] / exposure_time[1]
                    if speed >= 1:
                        return f"{speed:.1f}s"
                    else:
                        return f"1/{int(1/speed)}s"
            elif hasattr(exposure_time, '__float__'):  # Handle IFDRational and other numeric types
                speed = float(exposure_time)
                if speed >= 1:
                    return f"{speed:.1f}s"
                else:
                    return f"1/{int(1/speed)}s"
            elif isinstance(exposure_time, (int, float)):
                if exposure_time >= 1:
                    return f"{exposure_time:.1f}s"
                else:
                    return f"1/{int(1/exposure_time)}s"
        
        return 'Unavailable'
    
    def _get_iso_info(self, exif: Dict) -> str:
        """Extract ISO information from EXIF"""
        iso_fields = ['ISOSpeedRatings', 'ISO', 'PhotographicSensitivity']
        
        for field in iso_fields:
            iso = exif.get(field)
            if iso:
                if isinstance(iso, (list, tuple)) and len(iso) > 0:
                    return f"ISO {iso[0]}"
                elif isinstance(iso, (int, float)):
                    return f"ISO {int(iso)}"
        
        return 'Unavailable'
    
    def _get_focal_length_info(self, exif: Dict) -> str:
        """Extract focal length information from EXIF"""
        focal_length = exif.get('FocalLength')
        if focal_length:
            if isinstance(focal_length, tuple) and len(focal_length) == 2:
                fl = focal_length[0] / focal_length[1]
                return f"{fl:.0f}mm"
            elif hasattr(focal_length, '__float__'):  # Handle IFDRational and other numeric types
                return f"{float(focal_length):.0f}mm"
            elif isinstance(focal_length, (int, float)):
                return f"{focal_length:.0f}mm"
        
        return 'Unavailable'
    
    def _get_date_taken(self, exif: Dict) -> str:
        """Extract date taken from EXIF and format it human-readable"""
        date_taken = exif.get('DateTimeOriginal') or exif.get('DateTime')
        if date_taken:
            try:
                # EXIF format: "2025:02:02 00:50:29"
                from datetime import datetime
                dt = datetime.strptime(str(date_taken), '%Y:%m:%d %H:%M:%S')
                # Format as "February 2, 2025 at 12:50 AM"
                return dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                # If parsing fails, return as-is
                return str(date_taken)
        return 'Unavailable'
    
    def _get_dimensions(self, exif: Dict, img_size: tuple = None) -> str:
        """Extract image dimensions from EXIF or image file"""
        # Try EXIF first
        width = exif.get('ExifImageWidth')
        height = exif.get('ExifImageHeight')
        if width and height:
            return f"{width} x {height}"
        
        # Fall back to actual image size
        if img_size and len(img_size) == 2:
            return f"{img_size[0]} x {img_size[1]}"
        
        return 'Unavailable'
    
    def _get_default_exif(self) -> Dict[str, str]:
        """Return default EXIF data when extraction fails"""
        return {
            'camera': 'Unavailable',
            'lens': 'Unavailable',
            'aperture': 'Unavailable',
            'shutter_speed': 'Unavailable',
            'iso': 'Unavailable',
            'focal_length': 'Unavailable',
            'date_taken': 'Unavailable',
            'dimensions': 'Unavailable'
        }

