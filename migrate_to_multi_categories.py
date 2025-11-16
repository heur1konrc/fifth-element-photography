#!/usr/bin/env python3
"""
Migration script to convert single-category system to multi-category system.
Converts image_categories.json from {"filename": "category"} to {"filename": ["category"]}
"""

import json
import os
import shutil
from datetime import datetime

DATA_FILE = '/data/image_categories.json'
BACKUP_FILE = f'/data/image_categories_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

def migrate_categories():
    """Migrate from single category to multi-category format"""
    
    print("=" * 60)
    print("Multi-Category Migration Script")
    print("=" * 60)
    
    # Check if file exists
    if not os.path.exists(DATA_FILE):
        print(f"✗ File not found: {DATA_FILE}")
        print("Creating new multi-category file...")
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
        print("✓ Created empty multi-category file")
        return
    
    # Load existing data
    print(f"\n1. Loading existing data from {DATA_FILE}...")
    with open(DATA_FILE, 'r') as f:
        old_data = json.load(f)
    
    print(f"   Found {len(old_data)} images with category assignments")
    
    # Check if already migrated
    if old_data and isinstance(list(old_data.values())[0], list):
        print("\n✓ Data is already in multi-category format!")
        print("   No migration needed.")
        return
    
    # Create backup
    print(f"\n2. Creating backup at {BACKUP_FILE}...")
    shutil.copy2(DATA_FILE, BACKUP_FILE)
    print("   ✓ Backup created successfully")
    
    # Convert to multi-category format
    print("\n3. Converting to multi-category format...")
    new_data = {}
    for filename, category in old_data.items():
        if isinstance(category, str):
            # Convert single category string to list
            new_data[filename] = [category]
            print(f"   {filename}: '{category}' → ['{category}']")
        elif isinstance(category, list):
            # Already a list, keep as is
            new_data[filename] = category
        else:
            # Unknown format, default to 'other'
            new_data[filename] = ['other']
            print(f"   {filename}: (unknown format) → ['other']")
    
    # Save converted data
    print(f"\n4. Saving converted data to {DATA_FILE}...")
    with open(DATA_FILE, 'w') as f:
        json.dump(new_data, f, indent=2)
    print("   ✓ Data saved successfully")
    
    # Summary
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print(f"✓ Migrated {len(new_data)} images")
    print(f"✓ Backup saved to: {BACKUP_FILE}")
    print(f"✓ New format: Each image now has a list of categories")
    print("\nYou can now assign multiple categories to each image!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        migrate_categories()
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        print(f"   Backup file: {BACKUP_FILE}")
        raise

