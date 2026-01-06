#!/usr/bin/env python3
"""
Clean Image Descriptions
Removes excessive line breaks and formatting issues from image descriptions stored in JSON.
"""
import json
import os
import re
from datetime import datetime

def clean_html_description(html):
    """
    Aggressively clean HTML description to remove excessive line breaks and spacing.
    """
    if not html:
        return html
    
    # Remove all empty paragraphs (with any combination of whitespace, &nbsp;, <br>)
    html = re.sub(r'<p[^>]*>(?:\s|&nbsp;|<br\s*/?>)*</p>', '', html, flags=re.IGNORECASE)
    
    # Remove multiple consecutive <br> tags (keep max 1)
    html = re.sub(r'(<br\s*/?>[\s\n]*){2,}', '<br>', html, flags=re.IGNORECASE)
    
    # Remove ALL whitespace (including newlines) between closing and opening tags
    html = re.sub(r'>\s+<', '><', html)
    
    # Trim whitespace inside paragraph tags
    html = re.sub(r'<p[^>]*>\s+', '<p>', html, flags=re.IGNORECASE)
    html = re.sub(r'\s+</p>', '</p>', html, flags=re.IGNORECASE)
    
    # Remove leading/trailing whitespace
    html = html.strip()
    
    return html

def clean_descriptions_file(file_path, backup=True):
    """
    Clean all descriptions in the JSON file.
    
    Args:
        file_path: Path to image_descriptions.json
        backup: Whether to create a backup before cleaning
    
    Returns:
        dict with stats about cleaning operation
    """
    if not os.path.exists(file_path):
        return {'error': f'File not found: {file_path}'}
    
    # Load existing descriptions
    with open(file_path, 'r') as f:
        descriptions = json.load(f)
    
    # Create backup if requested
    if backup:
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w') as f:
            json.dump(descriptions, f, indent=2)
        print(f"✓ Backup created: {backup_path}")
    
    # Clean each description
    stats = {
        'total': len(descriptions),
        'cleaned': 0,
        'unchanged': 0,
        'empty': 0
    }
    
    cleaned_descriptions = {}
    
    for filename, description in descriptions.items():
        if not description or not description.strip():
            stats['empty'] += 1
            cleaned_descriptions[filename] = description
            continue
        
        cleaned = clean_html_description(description)
        
        if cleaned != description:
            stats['cleaned'] += 1
            print(f"✓ Cleaned: {filename}")
            print(f"  Before length: {len(description)} chars")
            print(f"  After length:  {len(cleaned)} chars")
        else:
            stats['unchanged'] += 1
        
        cleaned_descriptions[filename] = cleaned
    
    # Save cleaned descriptions
    with open(file_path, 'w') as f:
        json.dump(cleaned_descriptions, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"CLEANING COMPLETE")
    print(f"{'='*60}")
    print(f"Total descriptions: {stats['total']}")
    print(f"Cleaned: {stats['cleaned']}")
    print(f"Unchanged: {stats['unchanged']}")
    print(f"Empty: {stats['empty']}")
    
    return stats

if __name__ == '__main__':
    # Determine file path based on environment
    file_path = '/data/image_descriptions.json' if os.path.exists('/data') else 'image_descriptions.json'
    
    print(f"Cleaning descriptions in: {file_path}")
    print(f"{'='*60}\n")
    
    stats = clean_descriptions_file(file_path, backup=True)
    
    if 'error' in stats:
        print(f"ERROR: {stats['error']}")
        exit(1)
