#!/usr/bin/env python3
"""
Standalone backup script - DO NOT MODIFY MAIN APP
Can be executed via URL to create backups
"""

from flask import Flask, send_file, jsonify
import os
import tarfile
import tempfile
from datetime import datetime

backup_app = Flask(__name__)

@backup_app.route('/create_backup')
def create_backup():
    """Create comprehensive backup via URL"""
    try:
        # Create temporary directory for backup
        temp_dir = tempfile.mkdtemp()
        backup_filename = f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        with tarfile.open(backup_path, 'w:gz') as tar:
            # Add all source code files
            source_files = ['app.py', 'requirements.txt', 'README.md', 'backup.py']
            for file in source_files:
                file_path = os.path.join(project_root, file)
                if os.path.exists(file_path):
                    tar.add(file_path, arcname=file)
            
            # Add templates directory
            templates_dir = os.path.join(project_root, 'templates')
            if os.path.exists(templates_dir):
                tar.add(templates_dir, arcname='templates')
            
            # Add static directory (CSS, JS, images)
            static_dir = os.path.join(project_root, 'static')
            if os.path.exists(static_dir):
                tar.add(static_dir, arcname='static')
            
            # Add data directory (all data files and uploaded images)
            if os.path.exists('/data'):
                tar.add('/data', arcname='data')
        
        return send_file(backup_path, as_attachment=True, download_name=backup_filename, mimetype='application/gzip')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backup_app.route('/backup_status')
def backup_status():
    """Check backup system status"""
    return jsonify({
        'status': 'Backup system ready',
        'timestamp': datetime.now().isoformat(),
        'backup_url': '/create_backup'
    })

if __name__ == '__main__':
    backup_app.run(host='0.0.0.0', port=5001, debug=False)

