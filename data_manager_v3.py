"""
Data Manager V3 - Fifth Element Photography
Version: 3.0.0-alpha

This module provides a clean interface for all data persistence operations.
It handles reading from and writing to JSON data files, isolating the
application logic from the specifics of data storage.

All data operations go through this module to ensure consistency and
make future data storage changes easier.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


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
        self.images_dir = self.data_dir / "images"
        
        # Data file paths
        self.metadata_file = self.data_dir / "image_metadata.json"
        self.categories_file = self.data_dir / "image_categories.json"
        self.category_list_file = self.data_dir / "categories.json"
        self.featured_file = self.data_dir / "featured_image.json"
        self.hero_file = self.data_dir / "hero_image.json"
        
        # Ensure directories exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
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
            'categories': categories.get(filename, [])
        }
    
    def update_image_metadata(self, filename: str, title: Optional[str] = None, 
                             description: Optional[str] = None) -> bool:
        """
        Update an image's title and/or description.
        
        Args:
            filename: Image filename
            title: New title (optional)
            description: New description (optional)
            
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

