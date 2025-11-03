#!/usr/bin/env python3
"""
Main Program - Archaeological Site AI Agent

This is the main program that runs everything.
It's like the conductor of an orchestra - it tells all the other modules what to do!

How it works:
1. Downloads images from Google Drive
2. Analyzes them with AI to find artifacts
3. Creates a presentation script
4. Generates audio narration
5. Creates an HTML presentation with images and audio
6. Opens it in your browser!

Usage:
    python3 main.py 3                    # Download and analyze 3 most recent images
"""

import os
import sys
import argparse
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Import our modules
from archaeological_agent import config
from archaeological_agent.google_drive import GoogleDriveDownloader
from archaeological_agent.image_analyzer import ImageAnalyzer
from archaeological_agent.audio_generator import AudioGenerator
from archaeological_agent.presentation import create_presentation, open_in_browser


def main():
    """Main function - this is where the program starts!"""
    
    # Set up command line arguments (what the user can type)
    parser = argparse.ArgumentParser(
        description='Archaeological Site AI Agent - Analyzes drone photos and creates presentations'
    )
    
    parser.add_argument(
        'num_images',
        type=int,
        help='How many recent images to download and analyze (example: 3)'
    )
    
    parser.add_argument(
        '--openai-key',
        type=str,
        help='OpenAI API key (or set OPENAI_API_KEY environment variable)'
    )
    
    args = parser.parse_args()
    
    # Make sure number of images makes sense
    if args.num_images < 1:
        print("Error: Number of images must be at least 1")
        sys.exit(1)
    
    # Create a temporary folder for downloaded images
    temp_dir = tempfile.mkdtemp(prefix='archaeological_agent_')
    
    try:
        print(f"\n{'='*60}")
        print("Archaeological Site AI Agent - FLL Competition Project")
        print(f"{'='*60}\n")
        
        # Step 1: Download images from Google Drive
        print(f"Step 1: Downloading {args.num_images} most recent image(s) from Google Drive...")
        
        downloader = GoogleDriveDownloader()
        image_paths = downloader.download_recent_images(
            config.DRIVE_FOLDER_ID, args.num_images, temp_dir
        )
        
        if not image_paths:
            print("Error: No images downloaded!")
            return
        
        # Step 2: Analyze images with AI
        print(f"\nStep 2: Analyzing images for artifacts...")
        analyzer = ImageAnalyzer(api_key=args.openai_key)
        
        narration_result = analyzer.analyze_multiple_images(image_paths)
        
        # Get the narration text and JPG image paths
        if isinstance(narration_result, tuple):
            narration_text, jpg_image_paths = narration_result
        else:
            narration_text = narration_result
            jpg_image_paths = image_paths
        
        print(f"\nGenerated Presentation Script:")
        print(f"{'-'*60}")
        print(narration_text)
        print(f"{'-'*60}\n")
        
        # Step 3: Generate audio from the script
        print(f"Step 3: Generating audio narration...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_output = os.path.join(os.getcwd(), f"archaeological_narration_{timestamp}.mp3")
        
        audio_gen = AudioGenerator()
        if audio_gen.text_to_speech(narration_text, audio_output):
            print(f"✓ Audio file created: {audio_output}")
            
            # Step 4: Create HTML presentation
            print(f"\nStep 4: Creating presentation with images and audio...")
            presentation_path = f'presentation_{timestamp}.html'
            
            if create_presentation(jpg_image_paths, audio_output, presentation_path):
                # Step 5: Open in browser
                print(f"\nStep 5: Opening presentation in browser...")
                open_in_browser(presentation_path)
                
                print(f"\n{'='*60}")
                print("✓ All done! The presentation is ready!")
                print(f"{'='*60}")
                print(f"\nFiles created:")
                print(f"  - Audio: {audio_output}")
                print(f"  - Presentation: {presentation_path}")
                print(f"\nThe presentation is now open in your browser.")
                print(f"You can navigate images with arrow keys and play the audio when ready!")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"\n✓ Cleaned up temporary files")
        except Exception as e:
            print(f"Warning: Could not clean up temporary files: {e}")


if __name__ == '__main__':
    main()

