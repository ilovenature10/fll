"""
Image Analyzer Module

This module uses AI to look at images and identify archaeological artifacts.
It uses OpenAI's GPT-4 Vision model to "see" what's in the pictures.
"""

import os
import sys
import base64
from pathlib import Path
from typing import List, Dict, Optional

try:
    import openai
except ImportError:
    print("Error: OpenAI library not installed.")
    print("Run: pip3 install -r requirements.txt")
    sys.exit(1)

from . import config
from . import image_converter


class ImageAnalyzer:
    """
    Analyzes images using AI to find archaeological artifacts.
    
    This class uses OpenAI's vision AI to look at drone photos
    and identify things like coins, pottery, swords, bones, and stone drawings.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Set up the image analyzer.
        
        Args:
            api_key: Your OpenAI API key (or set OPENAI_API_KEY environment variable)
        """
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("\nError: OpenAI API key not found!")
            print("Please set OPENAI_API_KEY environment variable:")
            print("  export OPENAI_API_KEY='your-api-key-here'")
            print("\nOr get your API key from: https://platform.openai.com/api-keys")
            sys.exit(1)
        
        self.client = openai.OpenAI(api_key=api_key)
        print("✓ Initialized AI image analyzer")
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Look at one image and identify artifacts.
        
        This function:
        1. Makes sure the image is in JPG format
        2. Sends it to the AI to analyze
        3. Gets back a description of what artifacts were found
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with 'success' (True/False) and 'analysis' (description)
        """
        try:
            # Make sure image is JPG format (AI works best with JPG)
            jpg_path = image_converter.ensure_jpg_format(image_path)
            
            # Read the image file
            with open(jpg_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Figure out what type of image it is
            image_ext = Path(jpg_path).suffix.lower()
            if image_ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif image_ext == '.png':
                mime_type = 'image/png'
            else:
                mime_type = 'image/jpeg'  # Default to JPEG
            
            # Convert image to base64 (so we can send it to the AI)
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Ask the AI to analyze the image
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4 with vision capabilities
                messages=[
                    {
                        "role": "system",
                        "content": """You are analyzing drone photography of an archaeological discovery site. 
                        You need to identify specific artifacts that are visible in the images.
                        
                        The site contains these artifacts:
                        1. Stone drawings/carvings - created to simulate ancient earth materials and markings
                        2. Brass pot with lid - a complete brass vessel
                        3. A sword - an ancient weapon
                        4. Coins - including real modern coins (Penny, Dime) and drawings of ancient coins with suggested manufacturing years
                        5. Bone - skeletal remains
                        
                        Be factual and specific about what you observe."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Look at this drone photograph and tell me what artifacts you can see.
                                
                                Look for:
                                - Stone drawings or carvings
                                - A brass pot with lid
                                - A sword
                                - Coins (modern Penny, Dime, or ancient coin drawings - suggest years if visible)
                                - Bone
                                
                                Describe what you see factually - what's there, where things are, what condition they're in.
                                Only mention what you can clearly see. Don't make things up."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Get the AI's analysis
            analysis = response.choices[0].message.content
            return {'success': True, 'analysis': analysis}
        
        except Exception as e:
            print(f"Error analyzing image {image_path}: {e}")
            return {'success': False, 'analysis': f"Could not analyze image: {str(e)}"}
    
    def analyze_multiple_images(self, image_paths: List[str]):
        """
        Analyze several images and create a presentation script.
        
        This function:
        1. Looks at each image to find artifacts
        2. Combines all the findings
        3. Creates a presentation script (30-40 seconds) that sounds like a 7th grader
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Tuple of (narration_text, jpg_image_paths)
            - narration_text: The presentation script
            - jpg_image_paths: List of JPG image paths (for presentation)
        """
        print(f"\nAnalyzing {len(image_paths)} image(s)...")
        
        all_analyses = []
        jpg_image_paths = []  # Keep track of JPG versions for presentation
        
        # Analyze each image
        for i, image_path in enumerate(image_paths, 1):
            print(f"  Processing image {i}/{len(image_paths)}: {Path(image_path).name}")
            
            # Make sure it's JPG and get the JPG path
            jpg_path = image_converter.ensure_jpg_format(image_path)
            jpg_image_paths.append(jpg_path)
            
            # Analyze the image
            result = self.analyze_image(jpg_path)
            if result['success']:
                all_analyses.append(result['analysis'])
        
        # If no images were analyzed successfully
        if not all_analyses:
            return ("Unable to analyze any images.", jpg_image_paths)
        
        # Create a presentation script from all the analyses
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are creating a presentation script for a 7th grade girl to read to teachers and judges in an FLL innovation project.
                        The narration should be approximately 30 to 40 seconds when spoken at a normal, clear pace.
                        
                        Write like how a real 7th grade girl would present to teachers - clear, confident, and natural.
                        It should sound like a student presentation: organized, easy to understand, but still age-appropriate.
                        Use simple words that a 7th grader would use. Sound confident and informative, like presenting a school project.
                        Don't use fancy words or poetic language. Be clear and straightforward.
                        Keep sentences short and easy to understand. Sound enthusiastic about the project but professional."""
                    },
                    {
                        "role": "user",
                        "content": f"""Based on these drone photograph analyses, write a presentation script (30-40 seconds when spoken) that sounds like a 7th grade girl presenting to teachers:
                        
                        {chr(10).join(f'Drone Photo {i+1}: {analysis}' for i, analysis in enumerate(all_analyses))}
                        
                        The artifacts found are:
                        - Stone drawings/carvings
                        - A brass pot with lid
                        - A sword
                        - Coins: modern coins (Penny, Dime) and ancient coin drawings (with years if mentioned)
                        - Bone
                        
                        Write the narration so it:
                        1. Opens clearly - "Hi, I'm going to tell you about our archaeological discovery..."
                        2. Describes what the drone found in an organized way - talk about each artifact clearly
                        3. Explains what these artifacts tell us - connects them together in a simple, educational way
                        4. Ends with a clear conclusion about what we learned
                        
                        Write it like you're a 7th grade student presenting your FLL innovation project to teachers.
                        Be clear and organized, but still natural. Don't sound like you're reading from a textbook.
                        Sound confident and informative - like you're explaining your project to adults.
                        Use simple words. Be engaging but professional. This is for a school presentation.
                        Use the details from the analyses but explain them clearly for an audience.
                        If coins have dates mentioned, include them naturally in your explanation.
                        Keep it between 30-40 seconds when read at a normal pace."""
                    }
                ],
                max_tokens=500
            )
            
            narration_text = response.choices[0].message.content
            return (narration_text, jpg_image_paths)
        
        except Exception as e:
            print(f"Error generating presentation script: {e}")
            # If AI fails, just combine the analyses
            narration_text = "\n\n".join(all_analyses)
            return (narration_text, jpg_image_paths)

