"""
Navigation Database Module
Manages hierarchical navigation structure for the website
"""

import sqlite3
from typing import List, Dict, Optional
import json
import os

# Use /data directory for persistence on Railway
DB_DIR = os.environ.get('DB_DIR', '/data')
DB_PATH = os.path.join(DB_DIR, 'navigation.db')

def init_db():
    """Initialize the navigation database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Navigation items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nav_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            parent_id INTEGER,
            gallery_id INTEGER,
            url TEXT,
            order_index INTEGER NOT NULL DEFAULT 0,
            visible INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES nav_items(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_nav_items() -> List[Dict]:
    """Get all navigation items"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM nav_items 
        ORDER BY order_index ASC
    ''')
    
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def get_nav_tree() -> List[Dict]:
    """Get navigation items as a hierarchical tree structure"""
    all_items = get_all_nav_items()
    
    # Build a map of items by ID
    items_map = {item['id']: item for item in all_items}
    
    # Add children array to each item
    for item in all_items:
        item['children'] = []
    
    # Build the tree
    root_items = []
    for item in all_items:
        if item['parent_id'] is None:
            root_items.append(item)
        else:
            parent = items_map.get(item['parent_id'])
            if parent:
                parent['children'].append(item)
    
    return root_items

def add_nav_item(name: str, item_type: str, parent_id: Optional[int] = None, 
                 gallery_id: Optional[int] = None, url: Optional[str] = None,
                 order_index: int = 0) -> int:
    """Add a new navigation item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO nav_items (name, type, parent_id, gallery_id, url, order_index)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, item_type, parent_id, gallery_id, url, order_index))
    
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def update_nav_item(item_id: int, name: Optional[str] = None, 
                    parent_id: Optional[int] = None, order_index: Optional[int] = None,
                    visible: Optional[int] = None) -> bool:
    """Update a navigation item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if name is not None:
        updates.append('name = ?')
        params.append(name)
    if parent_id is not None:
        updates.append('parent_id = ?')
        params.append(parent_id)
    if order_index is not None:
        updates.append('order_index = ?')
        params.append(order_index)
    if visible is not None:
        updates.append('visible = ?')
        params.append(visible)
    
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(item_id)
        
        query = f"UPDATE nav_items SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()
    return True

def delete_nav_item(item_id: int) -> bool:
    """Delete a navigation item and its children"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM nav_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return True

def reorder_nav_items(item_orders: List[Dict]) -> bool:
    """
    Reorder navigation items
    item_orders: List of dicts with 'id' and 'order_index' keys
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for item in item_orders:
        cursor.execute('''
            UPDATE nav_items 
            SET order_index = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (item['order_index'], item['id']))
    
    conn.commit()
    conn.close()
    return True

def get_visible_nav_tree() -> List[Dict]:
    """Get only visible navigation items as a tree"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM nav_items 
        WHERE visible = 1
        ORDER BY order_index ASC
    ''')
    
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Build tree structure
    items_map = {item['id']: item for item in items}
    for item in items:
        item['children'] = []
    
    root_items = []
    for item in items:
        if item['parent_id'] is None:
            root_items.append(item)
        else:
            parent = items_map.get(item['parent_id'])
            if parent:
                parent['children'].append(item)
    
    return root_items

# Initialize database on import
init_db()
