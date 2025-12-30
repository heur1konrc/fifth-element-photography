import os
from PIL import Image, ImageStat, ImageEnhance

def get_watermark_path(color='white'):
    """Get path to watermark file based on color"""
    # In production on Railway, this should be /data/watermarks
    # For local dev/sandbox, we check local path first
    
    filename = f"WATERMARK_RCorey_{color.upper()}.png"
    
    # Check /data/watermarks first (Production)
    prod_path = os.path.join('/data/watermarks', filename)
    if os.path.exists(prod_path):
        return prod_path
        
    # Check local app directory (Sandbox/Dev)
    local_path = os.path.join(os.path.dirname(__file__), 'watermarks', filename)
    if os.path.exists(local_path):
        return local_path
        
    return None

def calculate_brightness(image_region):
    """
    Calculate average brightness of an image region.
    Returns value 0-255 (0=black, 255=white)
    """
    # Convert to grayscale
    grayscale = image_region.convert('L')
    stat = ImageStat.Stat(grayscale)
    return stat.mean[0]

def apply_watermark(image_path, output_path=None, position='bottom-right', size='medium', color_mode='auto', opacity=1.0):
    """
    Apply watermark to an image.
    
    Args:
        image_path (str): Path to source image
        output_path (str): Path to save result (defaults to overwriting source)
        position (str): 'bottom-right', 'bottom-left', 'top-right', 'top-left', 'center'
        size (str): 'small' (10%), 'medium' (20%), 'large' (30%) of image width
        color_mode (str): 'auto', 'white', 'black'
        opacity (float): 0.0 to 1.0
    """
    if output_path is None:
        output_path = image_path
        
    print(f"DEBUG: Applying watermark to {image_path}")
    
    try:
        # Open base image
        if not os.path.exists(image_path):
            print(f"DEBUG: Source image not found at {image_path}")
            return False
            
        base_image = Image.open(image_path).convert('RGBA')
        print(f"DEBUG: Opened source image. Size: {base_image.size}")
        width, height = base_image.size
        
        # Determine watermark size
        scale_factors = {'small': 0.15, 'medium': 0.25, 'large': 0.35}
        scale = scale_factors.get(size, 0.25)
        target_wm_width = int(width * scale)
        
        # Determine position coordinates
        padding = 5  # 5 pixels from edge
        
        # Define regions for brightness calculation if auto
        # We need to know where the watermark WILL go to check brightness there
        
        # Load watermark to get aspect ratio
        # First, determine which color to load if not auto
        wm_color = 'white' # Default
        if color_mode == 'black':
            wm_color = 'black'
            
        wm_path = get_watermark_path(wm_color)
        print(f"DEBUG: Using watermark file: {wm_path}")
        
        if not wm_path:
            print(f"Watermark file not found for color {wm_color}")
            return False
            
        wm_img = Image.open(wm_path).convert('RGBA')
        print(f"DEBUG: Opened watermark. Size: {wm_img.size}")
        wm_aspect = wm_img.height / wm_img.width
        target_wm_height = int(target_wm_width * wm_aspect)
        
        # Calculate coordinates
        x, y = 0, 0
        if position == 'bottom-right':
            x = width - target_wm_width - padding
            y = height - target_wm_height - padding
        elif position == 'bottom-left':
            x = padding
            y = height - target_wm_height - padding
        elif position == 'top-right':
            x = width - target_wm_width - padding
            y = padding
        elif position == 'top-left':
            x = padding
            y = padding
        elif position == 'center':
            x = (width - target_wm_width) // 2
            y = (height - target_wm_height) // 2
            
        # Smart Auto-Color Logic
        if color_mode == 'auto':
            # Crop the region where watermark will be
            region = base_image.crop((x, y, x + target_wm_width, y + target_wm_height))
            brightness = calculate_brightness(region)
            
            # If region is bright (>128), use black watermark. Else white.
            # We add a threshold buffer.
            if brightness > 140: 
                wm_color = 'black'
            else:
                wm_color = 'white'
                
            # Reload watermark if we guessed wrong initially
            wm_path = get_watermark_path(wm_color)
            wm_img = Image.open(wm_path).convert('RGBA')
            
        # Resize watermark
        wm_resized = wm_img.resize((target_wm_width, target_wm_height), Image.Resampling.LANCZOS)
        
        # Apply opacity
        if opacity < 1.0:
            alpha = wm_resized.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            wm_resized.putalpha(alpha)
            
        # Composite
        base_image.paste(wm_resized, (x, y), wm_resized)
        
        # Save result (convert back to RGB for JPEG)
        print(f"DEBUG: Saving to {output_path}")
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            base_image = base_image.convert('RGB')
            base_image.save(output_path, quality=95)
        else:
            base_image.save(output_path)
            
        print("DEBUG: Save successful")
        return True
        
    except Exception as e:
        print(f"Error applying watermark: {e}")
        return False
