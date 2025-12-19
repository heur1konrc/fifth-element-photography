"""
Gallery Database Helper
Manages galleries (collections of images with hero image)
"""
import sqlite3
import os
import json

DB_PATH = '/data/galleries.db' if os.path.exists('/data') else 'galleries.db'

def init_gallery_db():
    """Initialize gallery database tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Galleries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS galleries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            hero_image TEXT,
            description TEXT,
            display_order INTEGER DEFAULT 0,
            visible INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Gallery images (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gallery_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gallery_id INTEGER NOT NULL,
            image_filename TEXT NOT NULL,
            display_order INTEGER DEFAULT 0,
            FOREIGN KEY (gallery_id) REFERENCES galleries(id) ON DELETE CASCADE,
            UNIQUE(gallery_id, image_filename)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_gallery(name, slug, hero_image=None, description='', display_order=0):
    """Create a new gallery"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO galleries (name, slug, hero_image, description, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, slug, hero_image, description, display_order))
        conn.commit()
        gallery_id = cursor.lastrowid
        conn.close()
        return gallery_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_all_galleries():
    """Get all galleries ordered by display_order"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM galleries WHERE visible = 1 ORDER BY display_order, name')
    galleries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return galleries

def get_gallery_by_slug(slug):
    """Get gallery by slug"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM galleries WHERE slug = ?', (slug,))
    gallery = cursor.fetchone()
    conn.close()
    return dict(gallery) if gallery else None

def add_image_to_gallery(gallery_id, image_filename, display_order=0):
    """Add image to gallery"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO gallery_images (gallery_id, image_filename, display_order)
            VALUES (?, ?, ?)
        ''', (gallery_id, image_filename, display_order))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_gallery_images(gallery_id):
    """Get all images in a gallery"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT image_filename FROM gallery_images 
        WHERE gallery_id = ? 
        ORDER BY display_order, image_filename
    ''', (gallery_id,))
    images = [row[0] for row in cursor.fetchall()]
    conn.close()
    return images

def remove_image_from_gallery(gallery_id, image_filename):
    """Remove image from gallery"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gallery_images WHERE gallery_id = ? AND image_filename = ?', 
                   (gallery_id, image_filename))
    conn.commit()
    conn.close()

def update_gallery(gallery_id, **kwargs):
    """Update gallery fields"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'slug', 'hero_image', 'description', 'display_order', 'visible']
    updates = []
    values = []
    
    for field in allowed_fields:
        if field in kwargs:
            updates.append(f"{field} = ?")
            values.append(kwargs[field])
    
    if updates:
        values.append(gallery_id)
        cursor.execute(f"UPDATE galleries SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    
    conn.close()

def delete_gallery(gallery_id):
    """Delete gallery and all associations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM galleries WHERE id = ?', (gallery_id,))
    conn.commit()
    conn.close()

# Initialize on import
init_gallery_db()
