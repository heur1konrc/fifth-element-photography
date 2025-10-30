#!/usr/bin/env python3
"""
Initialize print ordering database on Railway deployment
Copies the local database to /data if it doesn't exist
"""
import os
import shutil
import sqlite3

def init_print_ordering_database():
    """Initialize print ordering database in /data directory"""
    
    # Source database (in project)
    source_db = os.path.join(os.path.dirname(__file__), 'database', 'print_ordering.db')
    
    # Target database (in /data persistent volume)
    target_db = '/data/print_ordering.db'
    
    # Ensure /data directory exists
    os.makedirs('/data', exist_ok=True)
    
    # If target doesn't exist, copy from source
    if not os.path.exists(target_db):
        if os.path.exists(source_db):
            print(f"Copying print ordering database to {target_db}")
            shutil.copy2(source_db, target_db)
            print("Print ordering database initialized successfully")
        else:
            print(f"Warning: Source database not found at {source_db}")
            print("Creating empty database with schema...")
            
            # Create database with schema
            schema_file = os.path.join(os.path.dirname(__file__), 'database', 'print_ordering_schema.sql')
            if os.path.exists(schema_file):
                conn = sqlite3.connect(target_db)
                with open(schema_file, 'r') as f:
                    conn.executescript(f.read())
                conn.close()
                print("Empty database created with schema")
            else:
                print(f"Error: Schema file not found at {schema_file}")
    else:
        print(f"Print ordering database already exists at {target_db}")

if __name__ == '__main__':
    init_print_ordering_database()

