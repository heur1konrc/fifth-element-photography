#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ubuntu/fifth-element-photography')

from pictorem_api import get_product_sizes

try:
    sizes = get_product_sizes('stretched-canvas')
    print(f"Success! Got {len(sizes)} sizes")
    for size in sizes[:3]:
        print(f"  - {size}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

