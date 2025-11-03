"""
Image Converter Module

This module converts images to JPG format.
It makes sure all images are in JPG so they work well with AI analysis.

If an image is already JPG, it uses it directly (no conversion needed).
If it's HEIC or another format, it converts it to JPG.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


def ensure_jpg_format(image_path: str) -> str:
    """
    Make sure an image is in JPG format.
    
    If the image is already JPG, return it as-is.
    If it's another format (like HEIC), convert it to JPG.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Path to a JPG image (same file if already JPG, or new converted file)
    """
    image_path_lower = image_path.lower()
    
    # If already JPG, use it directly - no conversion needed!
    if image_path_lower.endswith(('.jpg', '.jpeg')):
        return image_path
    
    # Not JPG? Convert it to JPG
    return convert_to_jpg(image_path)


def convert_to_jpg(image_path: str) -> str:
    """
    Convert any image format to JPG.
    
    This function tries different methods to convert images:
    1. First tries macOS sips (fastest on Mac)
    2. Then tries PIL/Pillow (works for most formats)
    
    Args:
        image_path: Path to the image to convert
        
    Returns:
        Path to the converted JPG file
    """
    print(f"  Converting to JPG: {Path(image_path).name}")
    
    # Method 1: Use macOS sips command (fastest on Mac)
    # sips is built into macOS, so it's really fast!
    try:
        base_name = Path(image_path).stem
        jpeg_path = os.path.join(
            os.path.dirname(image_path), 
            f"{base_name}.jpg"
        )
        
        # Use sips to convert to JPG
        result = subprocess.run(
            ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '95', 
             str(image_path), '--out', str(jpeg_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and os.path.exists(jpeg_path):
            print(f"  ✓ Converted to JPG using macOS sips: {Path(jpeg_path).name}")
            return jpeg_path
        else:
            raise Exception(f"sips conversion failed: {result.stderr}")
            
    except FileNotFoundError:
        print(f"  ⚠ sips command not found, trying alternative method...")
    except subprocess.TimeoutExpired:
        print(f"  ⚠ sips conversion timed out, trying alternative method...")
    except Exception as e:
        print(f"  ⚠ sips conversion failed ({str(e)[:50]}), trying alternative method...")
    
    # Method 2: Try PIL/Pillow (Python library that works for most formats)
    try:
        from PIL import Image
        
        # For HEIC files, we need special support
        image_path_lower = image_path.lower()
        if image_path_lower.endswith('.heic'):
            try:
                import pillow_heif
                pillow_heif.register_heif_opener()
            except ImportError:
                pass  # Try without it
        
        # Open and convert the image
        img = Image.open(image_path)
        rgb_img = img.convert('RGB')  # JPG needs RGB color
        
        # Save as JPG
        base_name = Path(image_path).stem
        jpeg_path = os.path.join(
            os.path.dirname(image_path), 
            f"{base_name}.jpg"
        )
        
        rgb_img.save(jpeg_path, 'JPEG', quality=95, optimize=True)
        print(f"  ✓ Converted to JPG using PIL: {Path(jpeg_path).name}")
        return jpeg_path
        
    except ImportError:
        print(f"  ⚠ PIL not available")
    except Exception as e:
        print(f"  ⚠ PIL conversion failed ({str(e)[:50]})")
    
    # If all methods fail, return original (might still work)
    print(f"  ⚠ Could not convert to JPG, using original format")
    return image_path

