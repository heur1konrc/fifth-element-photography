#!/usr/bin/env python3
"""
Master import script for all Fifth Element Photography products.
Runs all individual import scripts in sequence.
"""

import os
import sys
import subprocess

# List of all import scripts in order
IMPORT_SCRIPTS = [
    # Framed Canvas
    'import_125_framed_canvas.py',
    'import_150_framed_canvas.py',
    
    # Fine Art Paper
    'import_fine_art_paper.py',
    'import_fine_art_hot_press.py',
    'import_fine_art_cold_press.py',
    'import_fine_art_semi_glossy.py',
    'import_fine_art_metallic.py',
    'import_fine_art_glossy.py',
    'import_fine_art_somerset_velvet.py',
    
    # Foam Mounted
    'import_foam_mounted.py',
    
    # Metal
    'import_metal.py',
    
    # Peel and Stick
    'import_peel_and_stick.py',
    
    # Framed Fine Art Paper
    'import_framed_fine_art_0875.py',
    'import_framed_fine_art_125x0875.py',
    'import_framed_fine_art_mixed.py',
    'import_framed_fine_art_2x1062.py',
]

def main():
    print("=" * 60)
    print("FIFTH ELEMENT PHOTOGRAPHY - MASTER PRODUCT IMPORT")
    print("=" * 60)
    print()
    
    # First, initialize the new database
    print("Step 1: Initializing new database structure...")
    print("-" * 60)
    try:
        result = subprocess.run(
            [sys.executable, 'init_new_database.py'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED to initialize database")
        print(f"Error: {e.stderr}")
        return 1
    
    print()
    print("Step 2: Importing products...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    failed_scripts = []
    
    for i, script in enumerate(IMPORT_SCRIPTS, 1):
        print(f"[{i}/{len(IMPORT_SCRIPTS)}] Running {script}...")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ SUCCESS: {script}")
                print(result.stdout)
                successful += 1
            else:
                print(f"❌ FAILED: {script}")
                print(f"Error: {result.stderr}")
                failed += 1
                failed_scripts.append(script)
                
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT: {script}")
            failed += 1
            failed_scripts.append(script)
        except Exception as e:
            print(f"❌ ERROR: {script}")
            print(f"Exception: {str(e)}")
            failed += 1
            failed_scripts.append(script)
        
        print()
    
    # Summary
    print("=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {successful}/{len(IMPORT_SCRIPTS)}")
    print(f"❌ Failed: {failed}")
    
    if failed_scripts:
        print("\nFailed scripts:")
        for script in failed_scripts:
            print(f"  - {script}")
        return 1
    else:
        print("\n🎉 ALL IMPORTS COMPLETED SUCCESSFULLY!")
        
        # Show final product count
        try:
            import sqlite3
            conn = sqlite3.connect('/data/lumaprints_pricing.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(DISTINCT category) FROM products')
            categories = cursor.fetchone()[0]
            conn.close()
            
            print(f"\n📊 Database Summary:")
            print(f"   Total Products: {count}")
            print(f"   Categories: {categories}")
        except:
            pass
        
        return 0

if __name__ == '__main__':
    exit(main())

