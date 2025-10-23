#!/usr/bin/env python3.11
"""
Master Product Import Script
Runs all product import scripts in sequence
"""

import os
import sys
import subprocess

# List of all import scripts in order
IMPORT_SCRIPTS = [
    # Framed Canvas
    "import_125_framed_canvas.py",
    "import_150_framed_canvas.py",
    
    # Fine Art Paper
    "import_fine_art_paper.py",  # Archival Matte
    "import_fine_art_hot_press.py",
    "import_fine_art_cold_press.py",
    "import_fine_art_semi_glossy.py",
    "import_fine_art_metallic.py",
    "import_fine_art_glossy.py",
    "import_fine_art_somerset_velvet.py",
    
    # Foam-Mounted
    "import_foam_mounted.py",
    
    # Metal
    "import_metal.py",
    
    # Peel and Stick
    "import_peel_and_stick.py",
    
    # Framed Fine Art Paper
    "import_framed_fine_art_0875.py",
    "import_framed_fine_art_125x0875.py",
    "import_framed_fine_art_mixed.py",
    "import_framed_fine_art_2x1062.py",
]

def main():
    print("="*60)
    print("FIFTH ELEMENT PHOTOGRAPHY - MASTER PRODUCT IMPORT")
    print("="*60)
    print()
    
    total_scripts = len(IMPORT_SCRIPTS)
    successful = 0
    failed = []
    
    for i, script in enumerate(IMPORT_SCRIPTS, 1):
        print(f"\n[{i}/{total_scripts}] Running {script}...")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                ["python3.11", script],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            successful += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ FAILED: {script}")
            print(f"Error: {e.stderr}")
            failed.append(script)
        except FileNotFoundError:
            print(f"❌ SCRIPT NOT FOUND: {script}")
            failed.append(script)
    
    # Final summary
    print("\n" + "="*60)
    print("IMPORT COMPLETE")
    print("="*60)
    print(f"✅ Successful: {successful}/{total_scripts}")
    
    if failed:
        print(f"❌ Failed: {len(failed)}")
        print("\nFailed scripts:")
        for script in failed:
            print(f"  - {script}")
        sys.exit(1)
    else:
        print("\n🎉 ALL IMPORTS SUCCESSFUL!")
        print("\nYour product catalog is now fully loaded!")

if __name__ == "__main__":
    main()
