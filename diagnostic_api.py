"""
Diagnostic API - Check filesystem and database status
"""

from flask import jsonify
import os
from PIL import Image

def register_diagnostic_routes(app):
    """Register diagnostic routes"""
    
    @app.route('/api/diagnostic/filesystem')
    def diagnostic_filesystem():
        """Check what files exist in /data/ and /data/originals/"""
        try:
            result = {
                'data_dir': {
                    'exists': os.path.exists('/data'),
                    'files': []
                },
                'originals_dir': {
                    'exists': os.path.exists('/data/originals'),
                    'files': []
                }
            }
            
            # List files in /data/
            if os.path.exists('/data'):
                files = []
                for filename in os.listdir('/data'):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        filepath = os.path.join('/data', filename)
                        try:
                            img = Image.open(filepath)
                            width, height = img.size
                            files.append({
                                'filename': filename,
                                'dimensions': f'{width}x{height}',
                                'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2)
                            })
                        except:
                            files.append({
                                'filename': filename,
                                'error': 'Could not read image'
                            })
                result['data_dir']['files'] = files[:20]  # Limit to first 20
                result['data_dir']['total_count'] = len(files)
            
            # List files in /data/originals/
            if os.path.exists('/data/originals'):
                files = []
                for filename in os.listdir('/data/originals'):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        filepath = os.path.join('/data/originals', filename)
                        try:
                            img = Image.open(filepath)
                            width, height = img.size
                            files.append({
                                'filename': filename,
                                'dimensions': f'{width}x{height}',
                                'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2)
                            })
                        except:
                            files.append({
                                'filename': filename,
                                'error': 'Could not read image'
                            })
                result['originals_dir']['files'] = files[:20]  # Limit to first 20
                result['originals_dir']['total_count'] = len(files)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500
    
    @app.route('/api/diagnostic/image/<filename>')
    def diagnostic_image(filename):
        """Get detailed info about a specific image"""
        try:
            paths = {
                'web': f'/data/{filename}',
                'original': f'/data/originals/{filename}'
            }
            
            result = {}
            for key, path in paths.items():
                if os.path.exists(path):
                    try:
                        img = Image.open(path)
                        width, height = img.size
                        result[key] = {
                            'exists': True,
                            'path': path,
                            'dimensions': f'{width}x{height}',
                            'width': width,
                            'height': height,
                            'size_mb': round(os.path.getsize(path) / (1024 * 1024), 2),
                            'format': img.format
                        }
                    except Exception as e:
                        result[key] = {
                            'exists': True,
                            'path': path,
                            'error': str(e)
                        }
                else:
                    result[key] = {
                        'exists': False,
                        'path': path
                    }
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500

