"""
Database helper to provide consistent connection for import scripts.
Uses SQLite for local/Railway deployment.
"""

import sqlite3
import os

DB_PATH = '/data/lumaprints_pricing.db'

def get_db_connection():
    """Get database connection"""
    # Ensure /data directory exists
    os.makedirs('/data', exist_ok=True)
    return sqlite3.connect(DB_PATH)

def execute_insert(cursor, query, params):
    """
    Execute insert with parameter substitution.
    Converts PostgreSQL %s placeholders to SQLite ? placeholders.
    """
    # Convert %s to ?
    sqlite_query = query.replace('%s', '?')
    cursor.execute(sqlite_query, params)

