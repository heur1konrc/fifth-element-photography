"""
Migration script to populate navigation database from existing gallery categories
"""

from gallery_db import get_all_galleries
from navigation_db import add_nav_item, get_all_nav_items

def migrate_categories_to_navigation():
    """Migrate existing gallery categories to navigation system"""
    
    # Check if navigation already has items
    existing_nav = get_all_nav_items()
    if existing_nav:
        print(f"Navigation already has {len(existing_nav)} items. Skipping migration.")
        return
    
    # Get all galleries
    galleries = get_all_galleries()
    
    # Group galleries by category
    categories = {}
    uncategorized = []
    
    for gallery in galleries:
        if gallery.get('category'):
            cat = gallery['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(gallery)
        else:
            uncategorized.append(gallery)
    
    # Create navigation items for each category
    category_order = 0
    for category_name in sorted(categories.keys()):
        # Add category as top-level nav item
        category_id = add_nav_item(
            name=category_name,
            item_type='category',
            order_index=category_order
        )
        print(f"Created category: {category_name} (ID: {category_id})")
        
        # Add galleries under this category
        gallery_order = 0
        for gallery in categories[category_name]:
            add_nav_item(
                name=gallery['name'],
                item_type='gallery',
                parent_id=category_id,
                gallery_id=gallery['id'],
                order_index=gallery_order
            )
            print(f"  Added gallery: {gallery['name']}")
            gallery_order += 1
        
        category_order += 1
    
    # Handle uncategorized galleries (if any)
    if uncategorized:
        print(f"\nFound {len(uncategorized)} uncategorized galleries (not added to navigation)")
    
    print("\nMigration complete!")

if __name__ == '__main__':
    migrate_categories_to_navigation()
