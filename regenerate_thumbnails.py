#!/usr/bin/env python3
"""
Regenerate all thumbnails at new quality settings (800px, 95% quality).
Run this script on Railway after deploying the updated thumbnail generation code.
"""

import os
import sys
from pathlib import Path
from data_manager_v3 import DataManagerV3

def main():
    print("Starting thumbnail regeneration...")
    
    # Initialize data manager
    data_manager = DataManagerV3()
    
    # Get all images
    images_dir = Path('/data')
    thumbnails_dir = Path('/data/thumbnails')
    
    if not images_dir.exists():
        print("ERROR: /data directory not found")
        sys.exit(1)
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                   and os.path.isfile(images_dir / f)]
    
    print(f"Found {len(image_files)} images")
    
    # Delete existing thumbnails
    if thumbnails_dir.exists():
        print("Removing old thumbnails...")
        for thumb_file in os.listdir(thumbnails_dir):
            thumb_path = thumbnails_dir / thumb_file
            if thumb_path.is_file():
                thumb_path.unlink()
        print("Old thumbnails removed")
    
    # Regenerate all thumbnails
    success_count = 0
    error_count = 0
    
    for i, filename in enumerate(image_files, 1):
        print(f"Processing {i}/{len(image_files)}: {filename}...", end=' ')
        try:
            if data_manager.generate_thumbnail(filename):
                success_count += 1
                print("✓")
            else:
                error_count += 1
                print("✗")
        except Exception as e:
            error_count += 1
            print(f"✗ Error: {e}")
    
    print("\n" + "="*50)
    print(f"Regeneration complete!")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print("="*50)

if __name__ == '__main__':
    main()
