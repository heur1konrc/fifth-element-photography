#!/usr/bin/env python3
"""
Test script to verify all Lumaprints product categories have the correct number of options
"""

import json
import re

def test_canvas_sizes():
    """Test that canvas sizes are correct"""
    print("🧪 Testing Canvas Sizes...")
    
    try:
        with open('correct_canvas_sizes.json', 'r') as f:
            canvas_data = json.load(f)
        
        expected_counts = {
            '0.75in Stretched Canvas': 17,
            '1.25in Stretched Canvas': 31, 
            '1.50in Stretched Canvas': 27,
            'Rolled Canvas': 31  # Same as 1.25in
        }
        
        all_passed = True
        for product, expected_count in expected_counts.items():
            actual_count = canvas_data[product]['total_sizes']
            status = "✅" if actual_count == expected_count else "❌"
            print(f"  {status} {product}: {actual_count} sizes (expected {expected_count})")
            if actual_count != expected_count:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error testing canvas sizes: {e}")
        return False

def test_javascript_options():
    """Test JavaScript product options"""
    print("\n🧪 Testing JavaScript Product Options...")
    
    try:
        with open('static/js/order_print_lumaprints.js', 'r') as f:
            content = f.read()
        
        # Test Foam-mounted Print options (should be 9)
        foam_start = content.find('// Foam-mounted Print Category (ID: 104)')
        foam_end = content.find('// Framed Fine Art Paper Category (ID: 105)', foam_start)
        foam_section = content[foam_start:foam_end]
        foam_options = len(re.findall(r'{ id: 104\d+, name:', foam_section))
        
        foam_status = "✅" if foam_options == 9 else "❌"
        print(f"  {foam_status} Foam-mounted Print: {foam_options} options (expected 9)")
        
        # Test Framed Fine Art Paper options (should be 25)
        frame_start = content.find('// Framed Fine Art Paper Category (ID: 105)')
        frame_end = content.find('// Metal Category (ID: 106)', frame_start)
        frame_section = content[frame_start:frame_end]
        frame_options = len(re.findall(r'{ id: 105\d+, name:', frame_section))
        
        frame_status = "✅" if frame_options == 25 else "❌"
        print(f"  {frame_status} Framed Fine Art Paper: {frame_options} frame options (expected 25)")
        
        # Test Fine Art Paper options (should be 8, was reduced from 9)
        fap_start = content.find('// Fine Art Paper Category (ID: 103)')
        fap_end = content.find('// Foam-mounted Print Category (ID: 104)', fap_start)
        fap_section = content[fap_start:fap_end]
        fap_options = len(re.findall(r'{ id: 103\d+, name:', fap_section))
        
        fap_status = "✅" if fap_options == 8 else "❌"
        print(f"  {fap_status} Fine Art Paper: {fap_options} options (expected 8)")
        
        # Test Metal Print options (should be 2)
        metal_start = content.find('// Metal Category (ID: 106)')
        metal_end = content.find('// Peel and Stick Category (ID: 107)', metal_start)
        metal_section = content[metal_start:metal_end]
        metal_options = len(re.findall(r'{ id: 106\d+, name:', metal_section))
        
        metal_status = "✅" if metal_options == 2 else "❌"
        print(f"  {metal_status} Metal Print: {metal_options} options (expected 2)")
        
        # Test Peel and Stick options (should be 2)
        peel_start = content.find('// Peel and Stick Category (ID: 107)')
        peel_end = content.find('};', peel_start)
        peel_section = content[peel_start:peel_end]
        peel_options = len(re.findall(r'{ id: 107\d+, name:', peel_section))
        
        peel_status = "✅" if peel_options == 2 else "❌"
        print(f"  {peel_status} Peel and Stick: {peel_options} options (expected 2)")
        
        return (foam_options == 9 and frame_options == 25 and 
                fap_options == 8 and metal_options == 2 and peel_options == 2)
        
    except Exception as e:
        print(f"  ❌ Error testing JavaScript options: {e}")
        return False

def test_framed_canvas_options():
    """Test Framed Canvas frame options"""
    print("\n🧪 Testing Framed Canvas Frame Options...")
    
    try:
        with open('static/js/order_print_lumaprints.js', 'r') as f:
            content = f.read()
        
        # Test 0.75" Framed Canvas (should have 23 frame colors)
        canvas_075_pattern = r'id: 102001.*?frameColors: \[(.*?)\]'
        match = re.search(canvas_075_pattern, content, re.DOTALL)
        if match:
            frame_colors = re.findall(r'{ name:', match.group(1))
            canvas_075_count = len(frame_colors)
        else:
            canvas_075_count = 0
        
        canvas_075_status = "✅" if canvas_075_count == 23 else "❌"
        print(f"  {canvas_075_status} 0.75\" Framed Canvas: {canvas_075_count} frame colors (expected 23)")
        
        # Test 1.25" Framed Canvas (should have 3 frame colors)
        canvas_125_pattern = r'id: 102002.*?frameColors: \[(.*?)\]'
        match = re.search(canvas_125_pattern, content, re.DOTALL)
        if match:
            frame_colors = re.findall(r'{ name:', match.group(1))
            canvas_125_count = len(frame_colors)
        else:
            canvas_125_count = 0
        
        canvas_125_status = "✅" if canvas_125_count == 3 else "❌"
        print(f"  {canvas_125_status} 1.25\" Framed Canvas: {canvas_125_count} frame colors (expected 3)")
        
        # Test 1.50" Framed Canvas (should have 8 frame colors)
        canvas_150_pattern = r'id: 102003.*?frameColors: \[(.*?)\]'
        match = re.search(canvas_150_pattern, content, re.DOTALL)
        if match:
            frame_colors = re.findall(r'{ name:', match.group(1))
            canvas_150_count = len(frame_colors)
        else:
            canvas_150_count = 0
        
        canvas_150_status = "✅" if canvas_150_count == 8 else "❌"
        print(f"  {canvas_150_status} 1.50\" Framed Canvas: {canvas_150_count} frame colors (expected 8)")
        
        return (canvas_075_count == 23 and canvas_125_count == 3 and canvas_150_count == 8)
        
    except Exception as e:
        print(f"  ❌ Error testing framed canvas options: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 LUMAPRINTS PRODUCT OPTIONS VERIFICATION")
    print("=" * 50)
    
    canvas_test = test_canvas_sizes()
    js_test = test_javascript_options()
    framed_test = test_framed_canvas_options()
    
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    all_passed = canvas_test and js_test and framed_test
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! All product categories have the correct number of options.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    print(f"\nCanvas Sizes: {'✅ PASS' if canvas_test else '❌ FAIL'}")
    print(f"JavaScript Options: {'✅ PASS' if js_test else '❌ FAIL'}")
    print(f"Framed Canvas Options: {'✅ PASS' if framed_test else '❌ FAIL'}")
    
    return all_passed

if __name__ == "__main__":
    main()
