#!/usr/bin/env python3
"""
Create EXIF data table in database
"""
import sqlite3
import os

# Database path - use /tmp for local testing, will be /data on Railway
import sys
if os.path.exists('/data'):
    DB_PATH = '/data/image_exif.db'
else:
    DB_PATH = '/home/ubuntu/image_exif.db'
    print(f"Using local path: {DB_PATH}")

def create_exif_table():
    """Create EXIF data table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create EXIF table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_exif (
            filename TEXT PRIMARY KEY,
            model TEXT,
            lens TEXT,
            aperture TEXT,
            shutter_speed TEXT,
            iso TEXT,
            focal_length TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ EXIF table created in {DB_PATH}")

if __name__ == '__main__':
    create_exif_table()
