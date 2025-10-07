#!/usr/bin/env python3
"""
Generate correct canvas sizes based on requirements:
- 0.75in Canvas: 17 sizes
- 1.25in Canvas: 31 sizes  
- 1.50in Canvas: 27 sizes
"""

import json

def generate_canvas_sizes():
    """Generate the correct number of sizes for each canvas type"""
    
    # 0.75in Canvas - 17 sizes (constraints: 8-30 width, 10-30 height)
    canvas_075_sizes = [
        (8, 10), (8, 12), (9, 12), (10, 10), (10, 12), (10, 14),
        (11, 14), (12, 12), (12, 16), (14, 18), (16, 16), (16, 20),
        (18, 18), (20, 20), (20, 24), (24, 24), (30, 30)
    ]
    
    # 1.25in Canvas - 31 sizes (constraints: 8-45 width, 10-60 height)
    canvas_125_sizes = [
        (8, 10), (8, 12), (9, 12), (10, 10), (10, 12), (10, 14), (10, 20),
        (11, 14), (11, 17), (12, 12), (12, 16), (12, 18), (12, 24),
        (14, 18), (16, 16), (16, 20), (16, 24), (18, 18), (18, 24),
        (20, 20), (20, 24), (20, 30), (24, 24), (24, 30), (24, 36),
        (30, 30), (30, 40), (36, 36), (36, 48), (40, 40), (45, 60)
    ]
    
    # 1.50in Canvas - 27 sizes (constraints: 8-45 width, 10-60 height)
    canvas_150_sizes = [
        (8, 10), (8, 12), (9, 12), (10, 10), (10, 12), (10, 14), (10, 20),
        (11, 14), (11, 17), (12, 12), (12, 16), (12, 18), (12, 24),
        (14, 18), (16, 16), (16, 20), (16, 24), (18, 18), (18, 24),
        (20, 20), (20, 24), (20, 30), (24, 24), (24, 30), (30, 30),
        (36, 36), (40, 40)
    ]
    
    # Rolled Canvas - same as 1.25in for now
    rolled_canvas_sizes = canvas_125_sizes.copy()
    
    canvas_data = {
        "0.75in Stretched Canvas": {
            "subcategory_id": 101001,
            "constraints": {"min_width": 8, "max_width": 30, "min_height": 10, "max_height": 30},
            "available_sizes": [
                {"width": w, "height": h, "size_string": f"{w}x{h}", "wholesale_price": 15.00 + (w*h*0.1)}
                for w, h in canvas_075_sizes
            ],
            "total_sizes": len(canvas_075_sizes)
        },
        "1.25in Stretched Canvas": {
            "subcategory_id": 101002,
            "constraints": {"min_width": 8, "max_width": 45, "min_height": 10, "max_height": 60},
            "available_sizes": [
                {"width": w, "height": h, "size_string": f"{w}x{h}", "wholesale_price": 18.00 + (w*h*0.12)}
                for w, h in canvas_125_sizes
            ],
            "total_sizes": len(canvas_125_sizes)
        },
        "1.50in Stretched Canvas": {
            "subcategory_id": 101003,
            "constraints": {"min_width": 8, "max_width": 45, "min_height": 10, "max_height": 60},
            "available_sizes": [
                {"width": w, "height": h, "size_string": f"{w}x{h}", "wholesale_price": 20.00 + (w*h*0.14)}
                for w, h in canvas_150_sizes
            ],
            "total_sizes": len(canvas_150_sizes)
        },
        "Rolled Canvas": {
            "subcategory_id": 101005,
            "constraints": {"min_width": 8, "max_width": 45, "min_height": 10, "max_height": 60},
            "available_sizes": [
                {"width": w, "height": h, "size_string": f"{w}x{h}", "wholesale_price": 12.00 + (w*h*0.08)}
                for w, h in rolled_canvas_sizes
            ],
            "total_sizes": len(rolled_canvas_sizes)
        }
    }
    
    # Save the data
    with open('correct_canvas_sizes.json', 'w') as f:
        json.dump(canvas_data, f, indent=2)
    
    print("Generated correct canvas sizes:")
    for name, data in canvas_data.items():
        print(f"  {name}: {data['total_sizes']} sizes")
    
    return canvas_data

if __name__ == "__main__":
    generate_canvas_sizes()
