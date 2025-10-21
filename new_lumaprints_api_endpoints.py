# New API endpoints that use Lumaprints codes directly
# Add these to app.py to replace the old sub-options system

@app.route('/api/hierarchical/lumaprints-options/<int:product_type_id>/<int:level>', methods=['GET'])
def get_lumaprints_options(product_type_id, level):
    """Get available Lumaprints options by querying actual products"""
    try:
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        options = []
        
        if level == 1:
            # Get distinct Lumaprints subcategory IDs from products
            cursor.execute("""
                SELECT DISTINCT p.lumaprints_subcategory_id, 
                       MIN(p.name) as example_name
                FROM products p
                WHERE p.product_type_id = ? 
                  AND p.active = 1 
                  AND p.lumaprints_subcategory_id IS NOT NULL
                GROUP BY p.lumaprints_subcategory_id
                ORDER BY p.lumaprints_subcategory_id
            """, (product_type_id,))
            
            for row in cursor.fetchall():
                subcategory_id = row['lumaprints_subcategory_id']
                example_name = row['example_name']
                
                # Extract a readable label from the product name
                # Example: "Canvas 1.25" 8×10"" -> "1.25""
                label = extract_option_label(example_name, product_type_id, level)
                
                options.append({
                    'id': subcategory_id,  # Use Lumaprints code as ID
                    'value': label,
                    'lumaprints_code': subcategory_id
                })
        
        elif level == 2:
            # Get distinct options from lumaprints_options JSON field
            # This requires parsing JSON from all matching products
            parent_id = request.args.get('parent_id', type=int)
            if not parent_id:
                return jsonify({'success': False, 'error': 'parent_id required for level 2'}), 400
            
            cursor.execute("""
                SELECT DISTINCT p.lumaprints_options
                FROM products p
                WHERE p.product_type_id = ? 
                  AND p.lumaprints_subcategory_id = ?
                  AND p.active = 1
                  AND p.lumaprints_options IS NOT NULL
            """, (product_type_id, parent_id))
            
            # Collect all unique option values from JSON
            option_values = set()
            for row in cursor.fetchall():
                try:
                    opts = json.loads(row['lumaprints_options'])
                    # Extract the relevant option (mat_size, paper_type, etc.)
                    if isinstance(opts, dict):
                        for key, value in opts.items():
                            if key in ['mat_size', 'frame_color', 'paper_type']:
                                option_values.add((key, value))
                except:
                    continue
            
            # Convert to list of options
            for option_type, option_id in sorted(option_values):
                label = get_option_label(option_type, option_id)
                options.append({
                    'id': option_id,  # Use Lumaprints option ID
                    'value': label,
                    'option_type': option_type,
                    'lumaprints_code': option_id
                })
        
        conn.close()
        return jsonify({
            'success': True,
            'options': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/hierarchical/lumaprints-sizes', methods=['GET'])
def get_lumaprints_sizes():
    """Get available sizes using Lumaprints codes"""
    try:
        product_type_id = request.args.get('product_type_id', type=int)
        subcategory_id = request.args.get('subcategory_id', type=int)
        option_id = request.args.get('option_id', type=int)
        
        if not product_type_id:
            return jsonify({'success': False, 'error': 'product_type_id required'}), 400
        
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get global markup
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 150.0
        
        # Build query using Lumaprints codes
        query = """
            SELECT p.id, p.name, p.size, p.cost_price, c.name as category_name,
                   p.lumaprints_subcategory_id, p.lumaprints_options
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.active = 1 AND p.product_type_id = ?
        """
        params = [product_type_id]
        
        if subcategory_id:
            query += " AND p.lumaprints_subcategory_id = ?"
            params.append(subcategory_id)
        
        if option_id:
            # Filter by JSON option - need to check if option_id exists in lumaprints_options
            query += " AND p.lumaprints_options LIKE ?"
            params.append(f'%{option_id}%')
        
        query += " ORDER BY p.size"
        
        cursor.execute(query, params)
        
        products = []
        for row in cursor.fetchall():
            customer_price = row['cost_price'] * (markup_percentage / 100)
            
            products.append({
                'id': row['id'],
                'name': row['name'],
                'size': row['size'],
                'category_name': row['category_name'],
                'cost_price': float(row['cost_price']),
                'customer_price': round(customer_price, 2),
                'lumaprints_subcategory_id': row['lumaprints_subcategory_id'],
                'lumaprints_options': json.loads(row['lumaprints_options']) if row['lumaprints_options'] else {}
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'products': products,
            'markup_percentage': markup_percentage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def extract_option_label(product_name, product_type_id, level):
    """Extract a readable label from product name"""
    # Product type specific extraction logic
    if product_type_id == 1:  # Canvas
        if '0.75"' in product_name:
            return '0.75" Stretched Canvas'
        elif '1.25"' in product_name:
            return '1.25" Stretched Canvas'
        elif '1.5"' in product_name:
            return '1.5" Stretched Canvas'
    
    elif product_type_id == 4:  # Framed Fine Art
        if level == 1:  # Frame size
            if '0.875"' in product_name:
                # Extract color
                if 'Black' in product_name:
                    return '0.875" Black Frame'
                elif 'White' in product_name:
                    return '0.875" White Frame'
                elif 'Oak' in product_name:
                    return '0.875" Oak Frame'
            elif '1.25"' in product_name:
                if 'Black' in product_name:
                    return '1.25" Black Frame'
                elif 'White' in product_name:
                    return '1.25" White Frame'
                elif 'Oak' in product_name:
                    return '1.25" Oak Frame'
    
    # Default: return first part of name
    return product_name.split(' ')[0:3].join(' ')


def get_option_label(option_type, option_id):
    """Get human-readable label for Lumaprints option ID"""
    labels = {
        # Mat sizes
        64: 'No Mat',
        66: '1.5" Mat',
        67: '2.0" Mat',
        68: '2.5" Mat',
        69: '3.0" Mat',
        # Paper types
        27: 'Archival Matte',
        28: 'Hot Press',
        29: 'Cold Press',
        30: 'Semi-Gloss',
        31: 'Metallic',
        32: 'Glossy',
        33: 'Somerset Velvet',
        34: 'Canvas',
        # Frame colors
        12: 'Black',
        13: 'White',
        91: 'Oak'
    }
    return labels.get(option_id, f'Option {option_id}')

