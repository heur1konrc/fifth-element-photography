"""
Navigation Helper Functions
Provides navigation data for templates
"""

from navigation_db import get_visible_nav_tree

def get_navigation_for_template():
    """Get navigation structure formatted for template rendering"""
    nav_tree = get_visible_nav_tree()
    
    # Format for template use
    formatted_nav = []
    for category in nav_tree:
        category_data = {
            'id': category['id'],
            'name': category['name'],
            'type': category['type'],
            'url': category.get('url', '#'),
            'children': []
        }
        
        # Add children (galleries and links)
        for child in category.get('children', []):
            if child['type'] == 'gallery' and child.get('gallery_id'):
                # Get gallery slug from gallery_db
                from gallery_db import get_gallery_by_id
                gallery = get_gallery_by_id(child['gallery_id'])
                if gallery:
                    category_data['children'].append({
                        'id': child['id'],
                        'name': child['name'],
                        'url': f"/gallery/{gallery['slug']}",
                        'type': 'gallery',
                        'gallery_id': child['gallery_id']
                    })
            elif child['type'] == 'link' and child.get('url'):
                # Custom page link
                category_data['children'].append({
                    'id': child['id'],
                    'name': child['name'],
                    'url': child['url'],
                    'type': 'link'
                })
        
        formatted_nav.append(category_data)
    
    return formatted_nav
