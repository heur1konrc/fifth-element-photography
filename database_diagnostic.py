"""
Database diagnostic functions
"""

import sqlite3
import os

def diagnose_database():
    """Check what tables exist in the database"""
    db_path = '/data/lumaprints_pricing.db'
    
    result = {
        'database_exists': os.path.exists(db_path),
        'database_path': db_path,
        'tables': [],
        'error': None
    }
    
    if not result['database_exists']:
        result['error'] = 'Database file does not exist'
        return result
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [{'name': col[1], 'type': col[2]} for col in cursor.fetchall()]
            
            result['tables'].append({
                'name': table_name,
                'row_count': count,
                'columns': columns
            })
        
        conn.close()
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

