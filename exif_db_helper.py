"""
Helper functions for EXIF database operations
"""
import sqlite3
import os

# Database path - use /data on Railway, local path for development
if os.path.exists('/data'):
    DB_PATH = '/data/image_exif.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'image_exif.db')

def store_exif_in_db(filename, exif_data):
    """Store EXIF data in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO image_exif 
            (filename, model, lens, aperture, shutter_speed, iso, focal_length)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            exif_data.get('model', 'Unavailable'),
            exif_data.get('lens', 'Unavailable'),
            exif_data.get('aperture', 'Unavailable'),
            exif_data.get('shutter_speed', 'Unavailable'),
            exif_data.get('iso', 'Unavailable'),
            exif_data.get('focal_length', 'Unavailable')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Stored EXIF for {filename} in database")
        return True
    except Exception as e:
        print(f"❌ Error storing EXIF for {filename}: {e}")
        return False

def get_exif_from_db(filename):
    """Retrieve EXIF data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT model, lens, aperture, shutter_speed, iso, focal_length
            FROM image_exif
            WHERE filename = ?
        ''', (filename,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'model': result[0],
                'lens': result[1],
                'aperture': result[2],
                'shutter_speed': result[3],
                'iso': result[4],
                'focal_length': result[5]
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving EXIF for {filename}: {e}")
        return None

def get_all_exif_from_db():
    """Retrieve all EXIF data from database as a dictionary"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, model, lens, aperture, shutter_speed, iso, focal_length
            FROM image_exif
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        exif_dict = {}
        for row in results:
            exif_dict[row[0]] = {
                'model': row[1],
                'lens': row[2],
                'aperture': row[3],
                'shutter_speed': row[4],
                'iso': row[5],
                'focal_length': row[6]
            }
        
        return exif_dict
    except Exception as e:
        print(f"Error retrieving all EXIF: {e}")
        return {}

def delete_exif_from_db(filename):
    """Delete EXIF data for a specific image"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM image_exif WHERE filename = ?', (filename,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting EXIF for {filename}: {e}")
        return False
