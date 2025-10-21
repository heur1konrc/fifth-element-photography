# Add this to app.py after the other fix endpoints

@app.route('/restore-database-from-backup')
def restore_database_from_backup():
    """Restore database from the backup file in static folder"""
    import shutil
    import os
    
    try:
        # Source: backup file in static folder
        backup_file = 'static/lumaprints_pricing_restore.db'
        
        # Destination: persistent /data/ directory
        target_file = '/data/lumaprints_pricing.db'
        
        # Ensure /data directory exists
        os.makedirs('/data', exist_ok=True)
        
        # Check if backup file exists
        if not os.path.exists(backup_file):
            return f"""
            <h1>❌ Error</h1>
            <p>Backup file not found at {backup_file}</p>
            """, 404
        
        # Copy the backup to /data/
        shutil.copy2(backup_file, target_file)
        
        # Verify the restore
        import sqlite3
        conn = sqlite3.connect(target_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE active = 1")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup = cursor.fetchone()
        markup_value = markup[0] if markup else 'Not set'
        conn.close()
        
        return f"""
        <h1>✅ Database Restored Successfully!</h1>
        <p><strong>Products restored:</strong> {product_count}</p>
        <p><strong>Global markup:</strong> {markup_value}%</p>
        <p><strong>Database location:</strong> {target_file}</p>
        
        <h2>Next Steps:</h2>
        <ul>
            <li><a href="/admin/pricing">Check Pricing Admin</a></li>
            <li><a href="/hierarchical_order_form">Test Order Form</a></li>
        </ul>
        """
        
    except Exception as e:
        return f"""
        <h1>❌ Restore Failed</h1>
        <p>Error: {str(e)}</p>
        """, 500

