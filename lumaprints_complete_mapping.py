#!/usr/bin/env python3
"""
Complete Lumaprints Product Configuration Mapping
Based on official API documentation: https://api-docs.lumaprints.com/doc-420501
"""

# Complete subcategory mapping from Lumaprints API
LUMAPRINTS_SUBCATEGORIES = {
    # Rolled Canvas
    101005: {'category': 'Canvas', 'subcategory': 'Rolled Canvas'},
    
    # Stretched Canvas
    101001: {'category': 'Canvas', 'subcategory': '0.75" Stretched Canvas'},
    101002: {'category': 'Canvas', 'subcategory': '1.25" Stretched Canvas'},
    101003: {'category': 'Canvas', 'subcategory': '1.5" Stretched Canvas'},
    
    # Framed Canvas
    102001: {'category': 'Framed Canvas', 'subcategory': '0.75" Framed Canvas'},
    102002: {'category': 'Framed Canvas', 'subcategory': '1.25" Framed Canvas'},
    102003: {'category': 'Framed Canvas', 'subcategory': '1.5" Framed Canvas'},
    
    # Fine Art Paper (8 types)
    103001: {'category': 'Fine Art Paper', 'subcategory': 'Archival Matte Fine Art Paper'},
    103002: {'category': 'Fine Art Paper', 'subcategory': 'Hot Press Fine Art Paper'},
    103003: {'category': 'Fine Art Paper', 'subcategory': 'Cold Press Fine Art Paper'},
    103005: {'category': 'Fine Art Paper', 'subcategory': 'Semi-Glossy Fine Art Paper'},
    103006: {'category': 'Fine Art Paper', 'subcategory': 'Metallic Fine Art Paper'},
    103007: {'category': 'Fine Art Paper', 'subcategory': 'Glossy Fine Art Paper'},
    103008: {'category': 'Fine Art Paper', 'subcategory': 'Semi-Matte Fine Art Paper'},
    103009: {'category': 'Fine Art Paper', 'subcategory': 'Somerset Velvet Fine Art Paper'},
    
    # Framed Fine Art Paper (6 frame types)
    105001: {'category': 'Framed Fine Art Paper', 'subcategory': '0.875" Black Frame'},
    105002: {'category': 'Framed Fine Art Paper', 'subcategory': '0.875" White Frame'},
    105003: {'category': 'Framed Fine Art Paper', 'subcategory': '0.875" Oak Frame'},
    105005: {'category': 'Framed Fine Art Paper', 'subcategory': '1.25" Black Frame'},
    105006: {'category': 'Framed Fine Art Paper', 'subcategory': '1.25" White Frame'},
    105007: {'category': 'Framed Fine Art Paper', 'subcategory': '1.25" Oak Frame'},
    
    # Metal
    106001: {'category': 'Metal', 'subcategory': 'Metal Print'},
}

# Option codes for each product type
LUMAPRINTS_OPTIONS = {
    # Rolled Canvas (101005)
    101005: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'border_size': {
            19: '2 inch border plus 1 inch white space (default)',
            20: '1 inch border plus 1 inch white space',
            21: 'No border with 1 inch white space',
            22: 'Trimmed (No border, No white space)'
        }
    },
    
    # 0.75" Stretched Canvas (101001)
    101001: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'hanging_hardware': {
            4: 'Sawtooth Hanger installed (default)',
            5: 'Hanging Wire installed',
            6: 'Black Backboard backing with sawtooth installed',
            7: 'Black Backboard backing with hanging wire installed',
            8: 'Hanging Wire provided loose',
            133: 'Three-point Security Hardware installed'
        }
    },
    
    # 1.25" Stretched Canvas (101002)
    101002: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'hanging_hardware': {
            4: 'Sawtooth Hanger installed (default)'
        }
    },
    
    # 1.5" Stretched Canvas (101003)
    101003: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'hanging_hardware': {
            4: 'Sawtooth Hanger installed (default)',
            5: 'Hanging Wire installed',
            6: 'Black Backboard backing with sawtooth installed',
            7: 'Black Backboard backing with hanging wire installed',
            8: 'Hanging Wire provided loose',
            133: 'Three-point Security Hardware installed'
        },
        'canvas_underlayer': {
            9: 'None (default)',
            10: 'Foamcore Underlayer'
        }
    },
    
    # 0.75" Framed Canvas (102001)
    102001: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'hanging_hardware': {
            16: 'Hanging Wire installed (default)',
            17: 'Black Backboard backing with hanging wire installed',
            18: 'Hanging Hardware Provided Loose',
            134: 'Three-point Security Hardware installed'
        },
        'frame_style': {
            12: '0.75" Black Floating Frame (default)',
            13: '0.75" White Floating Frame',
            14: '0.75" Silver Floating Frame',
            15: '0.75" Gold Floating Frame'
        }
    },
    
    # 1.25" Framed Canvas (102002)
    102002: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'hanging_hardware': {
            28: 'Hanging Wire installed (default)'
        },
        'frame_style': {
            27: '1.25" Black Floating Frame (default)',
            91: '1.25" Oak Floating Frame',
            120: '1.25" Walnut Floating Frame'
        }
    },
    
    # 1.5" Framed Canvas (102003)
    102003: {
        'canvas_border': {
            1: 'Image Wrap (default)',
            2: 'Mirror Wrap',
            3: 'Solid Color'
        },
        'hanging_hardware': {
            16: 'Hanging Wire installed (default)',
            17: 'Black Backboard backing with hanging wire installed',
            18: 'Hanging Hardware Provided Loose',
            134: 'Three-point Security Hardware installed'
        },
        'frame_style': {
            23: '1.5" Black Floating Frame (default)',
            24: '1.5" White Floating Frame',
            25: '1.5" Silver Floating Frame',
            26: '1.5" Gold Floating Frame',
            92: '1.5" Oak Floating Frame'
        },
        'canvas_underlayer': {
            9: 'None (default)',
            10: 'Foamcore Underlayer'
        }
    },
    
    # Fine Art Paper (all types 103001-103009)
    'fine_art_paper_bleed': {
        36: '0.25" Bleed (0.25" on each side) (default)',
        37: '0.50" Bleed (0.50" on each side)',
        38: '1.00" Bleed (1.00" on each side)',
        39: 'No Bleed (Image goes to edge of paper)'
    },
    
    # Metal Print (106001)
    106001: {
        'metal_surface': {
            29: 'Glossy White (default)',
            30: 'Glossy Silver'
        },
        'hanging_hardware': {
            31: 'Inset Frame (default)',
            32: 'Metal Easel',
            33: 'Small (3/4 inch) Stainless Steel Mounting Posts',
            34: 'Large (1 inch) Stainless Steel Mounting Posts',
            35: 'None'
        }
    }
}

# Default options for each subcategory
LUMAPRINTS_DEFAULTS = {
    101005: [1, 19],  # Rolled Canvas: Image Wrap, 2" border
    101001: [1, 4],   # 0.75" Canvas: Image Wrap, Sawtooth Hanger
    101002: [1, 4],   # 1.25" Canvas: Image Wrap, Sawtooth Hanger
    101003: [1, 4, 9], # 1.5" Canvas: Image Wrap, Sawtooth Hanger, No Underlayer
    102001: [1, 16, 12], # 0.75" Framed: Image Wrap, Hanging Wire, Black Frame
    102002: [1, 28, 27], # 1.25" Framed: Image Wrap, Hanging Wire, Black Frame
    102003: [1, 16, 23, 9], # 1.5" Framed: Image Wrap, Hanging Wire, Black Frame, No Underlayer
    103001: [36], # Fine Art Paper: 0.25" Bleed
    103002: [36], # Fine Art Paper: 0.25" Bleed
    103003: [36], # Fine Art Paper: 0.25" Bleed
    103005: [36], # Fine Art Paper: 0.25" Bleed
    103006: [36], # Fine Art Paper: 0.25" Bleed
    103007: [36], # Fine Art Paper: 0.25" Bleed
    103008: [36], # Fine Art Paper: 0.25" Bleed
    103009: [36], # Fine Art Paper: 0.25" Bleed
    106001: [29, 31], # Metal: Glossy White, Inset Frame
}

def get_subcategory_info(subcategory_id):
    """Get category and subcategory info for a Lumaprints subcategory ID"""
    return LUMAPRINTS_SUBCATEGORIES.get(subcategory_id, {})

def get_subcategory_options(subcategory_id):
    """Get all available options for a subcategory"""
    return LUMAPRINTS_OPTIONS.get(subcategory_id, {})

def get_default_options(subcategory_id):
    """Get default option IDs for a subcategory"""
    return LUMAPRINTS_DEFAULTS.get(subcategory_id, [])

if __name__ == "__main__":
    print("=== LUMAPRINTS COMPLETE PRODUCT MAPPING ===")
    print(f"Total subcategories: {len(LUMAPRINTS_SUBCATEGORIES)}")
    
    for subcat_id, info in LUMAPRINTS_SUBCATEGORIES.items():
        print(f"{subcat_id}: {info['category']} - {info['subcategory']}")
        options = get_subcategory_options(subcat_id)
        if options:
            print(f"  Options: {len(options)} option groups")
        defaults = get_default_options(subcat_id)
        if defaults:
            print(f"  Defaults: {defaults}")
        print()
