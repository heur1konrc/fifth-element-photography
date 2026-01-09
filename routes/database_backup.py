from flask import Blueprint, jsonify, request, send_file, render_template
import os
import shutil
from datetime import datetime
import glob

database_backup_bp = Blueprint('database_backup', __name__)

# Database paths
DATABASES = {
    'print_ordering': '/data/print_ordering.db',
    'pricing': '/data/pricing.db',
    'image_descriptions': '/data/image_descriptions.json'
}

BACKUP_DIR = '/data/backups'

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)


@database_backup_bp.route('/admin/database-backup')
def database_backup_page():
    """Render the database backup admin page"""
    return render_template('admin/database_backup.html')


@database_backup_bp.route('/api/database/backup/create', methods=['POST'])
def create_backup():
    """Create timestamped backups of all databases"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backed_up = []
        
        for db_name, db_path in DATABASES.items():
            if os.path.exists(db_path):
                # Create backup filename
                backup_filename = f"{db_name}_{timestamp}{os.path.splitext(db_path)[1]}"
                backup_path = os.path.join(BACKUP_DIR, backup_filename)
                
                # Copy database to backup
                shutil.copy2(db_path, backup_path)
                backed_up.append({
                    'database': db_name,
                    'backup_file': backup_filename,
                    'size': os.path.getsize(backup_path)
                })
        
        return jsonify({
            'success': True,
            'message': f'Created backups for {len(backed_up)} databases',
            'backups': backed_up,
            'timestamp': timestamp
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_backup_bp.route('/api/database/backup/list', methods=['GET'])
def list_backups():
    """List all available backups"""
    try:
        backups = []
        
        # Get all backup files
        backup_files = glob.glob(os.path.join(BACKUP_DIR, '*'))
        
        for backup_file in sorted(backup_files, reverse=True):
            filename = os.path.basename(backup_file)
            # Parse database name and timestamp from filename
            # Format: database_name_YYYYMMDD_HHMMSS.ext
            parts = filename.rsplit('_', 2)
            if len(parts) >= 3:
                db_name = parts[0]
                timestamp_str = f"{parts[1]}_{parts[2].split('.')[0]}"
                
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    backups.append({
                        'filename': filename,
                        'database': db_name,
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'size': os.path.getsize(backup_file),
                        'path': backup_file
                    })
                except ValueError:
                    # Skip files that don't match the expected format
                    continue
        
        # Group backups by timestamp
        grouped = {}
        for backup in backups:
            ts = backup['timestamp']
            if ts not in grouped:
                grouped[ts] = []
            grouped[ts].append(backup)
        
        return jsonify({
            'success': True,
            'backups': grouped,
            'total': len(backups)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_backup_bp.route('/api/database/backup/restore', methods=['POST'])
def restore_backup():
    """Restore databases from a backup timestamp"""
    try:
        data = request.json
        timestamp = data.get('timestamp')
        
        if not timestamp:
            return jsonify({
                'success': False,
                'error': 'Timestamp is required'
            }), 400
        
        # Convert timestamp format for filename matching
        timestamp_for_file = timestamp.replace('-', '').replace(':', '').replace(' ', '_')
        
        restored = []
        
        for db_name, db_path in DATABASES.items():
            # Find backup file for this database and timestamp
            pattern = f"{db_name}_{timestamp_for_file}*"
            backup_files = glob.glob(os.path.join(BACKUP_DIR, pattern))
            
            if backup_files:
                backup_file = backup_files[0]
                
                # Create a safety backup of current database before restoring
                safety_backup = f"{db_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if os.path.exists(db_path):
                    shutil.copy2(db_path, safety_backup)
                
                # Restore from backup
                shutil.copy2(backup_file, db_path)
                
                restored.append({
                    'database': db_name,
                    'restored_from': os.path.basename(backup_file),
                    'safety_backup': os.path.basename(safety_backup)
                })
        
        if not restored:
            return jsonify({
                'success': False,
                'error': f'No backups found for timestamp {timestamp}'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'Restored {len(restored)} databases from backup',
            'restored': restored
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_backup_bp.route('/api/database/backup/delete', methods=['POST'])
def delete_backup():
    """Delete a specific backup"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': 'Filename is required'
            }), 400
        
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            return jsonify({
                'success': False,
                'error': 'Backup file not found'
            }), 404
        
        os.remove(backup_path)
        
        return jsonify({
            'success': True,
            'message': f'Deleted backup {filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
