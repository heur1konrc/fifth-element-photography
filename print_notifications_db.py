"""
Database module for print availability notification requests
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = '/data/print_notifications.db'

def init_db():
    """Initialize the print notifications database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS print_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            image_title TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notified BOOLEAN DEFAULT 0,
            notified_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_notification_request(image_filename, image_title, first_name, last_name, email):
    """Add a new notification request"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO print_notifications 
        (image_filename, image_title, first_name, last_name, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (image_filename, image_title, first_name, last_name, email))
    
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return request_id

def get_pending_notifications(image_filename):
    """Get all pending notifications for an image"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM print_notifications 
        WHERE image_filename = ? AND notified = 0
        ORDER BY requested_at DESC
    ''', (image_filename,))
    
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notifications

def mark_as_notified(notification_id):
    """Mark a notification as sent"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE print_notifications 
        SET notified = 1, notified_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (notification_id,))
    
    conn.commit()
    conn.close()

def get_all_pending_notifications():
    """Get all pending notifications grouped by image"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM print_notifications 
        WHERE notified = 0
        ORDER BY image_filename, requested_at DESC
    ''')
    
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notifications

def get_all_notification_requests():
    """Get all notification requests"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, image_filename, image_title, first_name, last_name, email, 
               requested_at as created_at, notified
        FROM print_notifications
        ORDER BY requested_at DESC
    ''')
    
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notifications

def delete_notification_request(request_id):
    """Delete a notification request"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM print_notifications WHERE id = ?', (request_id,))
    
    conn.commit()
    conn.close()
