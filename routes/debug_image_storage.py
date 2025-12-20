from flask import Blueprint, jsonify
import os
import glob

debug_storage_bp = Blueprint('debug_storage', __name__)

@debug_storage_bp.route('/admin/debug/storage', methods=['GET'])
def debug_storage():
    """Debug endpoint to check where images are actually stored"""
    
    results = {
        'data_dir_exists': os.path.exists('/data'),
        'data_dir_contents': [],
        'originals_dir_exists': os.path.exists('/data/originals'),
        'originals_dir_contents': [],
        'image_count_in_data': 0,
        'image_count_in_originals': 0,
        'sample_files': []
    }
    
    # Check /data directory
    if os.path.exists('/data'):
        try:
            results['data_dir_contents'] = os.listdir('/data')[:50]  # First 50 items
            image_files = glob.glob('/data/*.jpg') + glob.glob('/data/*.jpeg') + glob.glob('/data/*.png')
            results['image_count_in_data'] = len(image_files)
            results['sample_files'].extend(image_files[:5])
        except Exception as e:
            results['data_error'] = str(e)
    
    # Check /data/originals directory
    if os.path.exists('/data/originals'):
        try:
            results['originals_dir_contents'] = os.listdir('/data/originals')[:50]
            image_files = glob.glob('/data/originals/*.jpg') + glob.glob('/data/originals/*.jpeg') + glob.glob('/data/originals/*.png')
            results['image_count_in_originals'] = len(image_files)
            results['sample_files'].extend(image_files[:5])
        except Exception as e:
            results['originals_error'] = str(e)
    
    # Check for Fall_Leaves-2.jpg specifically
    fall_leaves_paths = [
        '/data/Fall_Leaves-2.jpg',
        '/data/originals/Fall_Leaves-2.jpg',
        '/data/fall_leaves-2.jpg',
        '/data/originals/fall_leaves-2.jpg'
    ]
    
    results['fall_leaves_check'] = {}
    for path in fall_leaves_paths:
        results['fall_leaves_check'][path] = os.path.exists(path)
    
    return jsonify(results)
