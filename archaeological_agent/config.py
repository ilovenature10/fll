"""
Configuration file - All the settings for the archaeological agent

This file contains all the constants and settings that the program uses.
Think of it like a settings page - everything is defined in one place!
"""

# Google Drive folder ID for the FLL project
# This tells the program which folder to look in on Google Drive
DRIVE_FOLDER_ID = '1G0Pi9LF9rAHa9nWKO-EInp1MkgYx_wkM'

# What types of image files we can work with
# These are the file extensions we recognize as images
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg',  # Standard JPEG images
    '.png',           # PNG images
    '.heic', '.HEIC', # iPhone HEIC format
    '.gif',           # GIF images
    '.bmp',           # Bitmap images
    '.webp'           # WebP images
}

# What artifacts we're looking for in the images
# These are the things the AI should try to find
ARTIFACTS_TO_DETECT = [
    # Coins and money
    'coin', 'coins', 'penny', 'dime', 'currency', 'money',
    
    # Pottery and vessels
    'brass pot', 'brass lid', 'brass vessel', 'ceramic vessel',
    
    # Weapons
    'sword', 'blade', 'weapon',
    
    # Remains
    'bone', 'bones', 'skeletal remains',
    
    # Art and drawings
    'stone drawing', 'stone carving', 'petroglyph', 'engraving', 'rock art'
]

# Google API permissions (scopes)
# These tell Google what we need permission to do
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

