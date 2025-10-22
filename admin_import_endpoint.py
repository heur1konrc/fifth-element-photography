"""
Admin endpoint to run the Lumaprints product import on production.
This allows importing the database without shell access.
"""

from flask import jsonify
import subprocess
import os

def run_import_endpoint():
    """Execute the import script and return results"""
    try:
        # Change to the app directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Run the import script
        result = subprocess.run(
            ['python3', 'import_all_lumaprints_products.py'],
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Import script timed out after 5 minutes'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def check_import_status():
    """Check if products have been imported"""
    try:
        import sqlite3
        
        db_path = '/data/lumaprints_pricing.db'
        
        if not os.path.exists(db_path):
            return jsonify({
                'imported': False,
                'message': 'Database file does not exist',
                'db_path': db_path
            })
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check product count
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]
        
        # Check product types
        cursor.execute('SELECT COUNT(*) FROM product_types')
        type_count = cursor.fetchone()[0]
        
        # Check categories
        cursor.execute('SELECT COUNT(*) FROM categories')
        category_count = cursor.fetchone()[0]
        
        # Get breakdown by product type
        cursor.execute('''
            SELECT pt.name, COUNT(p.id)
            FROM product_types pt
            LEFT JOIN products p ON p.product_type_id = pt.id
            GROUP BY pt.id
            ORDER BY pt.display_order
        ''')
        breakdown = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'imported': product_count > 0,
            'product_count': product_count,
            'type_count': type_count,
            'category_count': category_count,
            'breakdown': [{'type': row[0], 'count': row[1]} for row in breakdown],
            'db_path': db_path
        })
        
    except Exception as e:
        return jsonify({
            'imported': False,
            'error': str(e)
        }), 500


def register_import_routes(app):
    """Register admin import routes"""
    
    @app.route('/admin/import-lumaprints-products', methods=['POST'])
    def admin_import_products():
        """Run the Lumaprints product import"""
        # Add authentication check here if needed
        return run_import_endpoint()
    
    @app.route('/admin/import-status', methods=['GET'])
    def admin_import_status():
        """Check import status"""
        return check_import_status()
    
    @app.route('/admin/import-interface', methods=['GET'])
    def admin_import_interface():
        """Simple HTML interface for running import"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lumaprints Product Import</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 40px; background: #f5f5f5; }
                .container { max-width: 800px; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status-box { padding: 20px; margin: 20px 0; border-radius: 5px; }
                .status-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                .status-error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
                .status-info { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
                pre { background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto; }
                .btn-import { font-size: 18px; padding: 12px 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4">🚀 Lumaprints Product Import</h1>
                
                <div id="status-display"></div>
                
                <div class="mb-4">
                    <button class="btn btn-primary btn-import" onclick="checkStatus()">
                        <i class="fas fa-info-circle"></i> Check Import Status
                    </button>
                    <button class="btn btn-success btn-import ms-2" onclick="runImport()">
                        <i class="fas fa-download"></i> Run Import
                    </button>
                </div>
                
                <div id="output-display"></div>
            </div>
            
            <script>
                async function checkStatus() {
                    const statusDiv = document.getElementById('status-display');
                    statusDiv.innerHTML = '<div class="status-box status-info">Checking status...</div>';
                    
                    try {
                        const response = await fetch('/admin/import-status');
                        const data = await response.json();
                        
                        if (data.imported) {
                            let html = '<div class="status-box status-success">';
                            html += '<h4>✅ Products Imported</h4>';
                            html += `<p><strong>Total Products:</strong> ${data.product_count}</p>`;
                            html += `<p><strong>Product Types:</strong> ${data.type_count}</p>`;
                            html += `<p><strong>Categories:</strong> ${data.category_count}</p>`;
                            html += '<h5>Breakdown:</h5><ul>';
                            data.breakdown.forEach(item => {
                                html += `<li>${item.type}: ${item.count} products</li>`;
                            });
                            html += '</ul></div>';
                            statusDiv.innerHTML = html;
                        } else {
                            statusDiv.innerHTML = '<div class="status-box status-error"><h4>❌ No Products Found</h4><p>Database is empty or not initialized. Click "Run Import" to populate.</p></div>';
                        }
                    } catch (error) {
                        statusDiv.innerHTML = `<div class="status-box status-error"><h4>Error</h4><p>${error.message}</p></div>`;
                    }
                }
                
                async function runImport() {
                    const outputDiv = document.getElementById('output-display');
                    const statusDiv = document.getElementById('status-display');
                    
                    statusDiv.innerHTML = '<div class="status-box status-info">Running import... This may take a few minutes.</div>';
                    outputDiv.innerHTML = '';
                    
                    try {
                        const response = await fetch('/admin/import-lumaprints-products', {
                            method: 'POST'
                        });
                        const data = await response.json();
                        
                        if (data.success) {
                            statusDiv.innerHTML = '<div class="status-box status-success"><h4>✅ Import Completed Successfully!</h4></div>';
                            outputDiv.innerHTML = '<h5>Import Output:</h5><pre>' + data.output + '</pre>';
                            
                            // Auto-check status after import
                            setTimeout(checkStatus, 1000);
                        } else {
                            statusDiv.innerHTML = '<div class="status-box status-error"><h4>❌ Import Failed</h4></div>';
                            outputDiv.innerHTML = '<h5>Error Output:</h5><pre>' + (data.error || data.output) + '</pre>';
                        }
                    } catch (error) {
                        statusDiv.innerHTML = '<div class="status-box status-error"><h4>Error</h4><p>' + error.message + '</p></div>';
                    }
                }
                
                // Check status on page load
                checkStatus();
            </script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        </body>
        </html>
        '''

