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
    
    def extract_artifacts(self, all_analyses: List[str]) -> List[Dict]:
        """
        Extract structured artifact information from analyses.
        
        Args:
            all_analyses: List of analysis text strings
            
        Returns:
            List of dictionaries with artifact information
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are extracting structured information about archaeological artifacts from image analyses.
                        Return a JSON array of artifacts, each with: name, time_period, country_of_origin, and additional_info.
                        Time period should be an estimated period (e.g., "Ancient Roman (100-300 CE)", "Modern (2024)", "Medieval (1000-1500 CE)", "Unknown").
                        Country of origin should be the most likely country/region where this type of artifact was typically made (e.g., "Roman Empire", "United States", "Unknown").
                        Additional info should include condition, location, or other relevant details."""
                    },
                    {
                        "role": "user",
                        "content": f"""Extract all artifacts mentioned in these analyses and return as JSON array.
                        For each artifact, provide:
                        - name: The artifact name (e.g., "Coin", "Brass Pot", "Sword", "Bone", "Stone Drawing")
                        - time_period: Estimated time period when it was made (e.g., "Ancient Roman (100-300 CE)", "Modern (2024)", "Medieval (1000-1500 CE)", "Unknown" or specific year/range if mentioned)
                        - country_of_origin: Most likely country or region of origin based on the artifact type and any visible characteristics (e.g., "Roman Empire", "United States", "Ancient Greece", "Unknown")
                        - additional_info: Any relevant details (condition, location, description, etc.)
                        
                        Use your knowledge of archaeology and history to estimate time periods and countries of origin when not explicitly stated.
                        For example:
                        - Modern US coins (Penny, Dime) → "Modern (2000-2024)" / "United States"
                        - Ancient Roman-style coins → "Ancient Roman (100-300 CE)" / "Roman Empire"
                        - Brass vessels → "Medieval to Modern" / "Various (Middle East, Europe)"
                        - Swords → "Medieval to Ancient" / "Europe or Middle East"
                        - Stone drawings/carvings → "Prehistoric to Ancient" / "Various"
                        
                        Analyses:
                        {chr(10).join(f'Analysis {i+1}: {analysis}' for i, analysis in enumerate(all_analyses))}
                        
                        Return a JSON object with an "artifacts" key containing an array. Example format:
                        {{
                            "artifacts": [
                                {{"name": "Coin", "time_period": "Modern (2024)", "country_of_origin": "United States", "additional_info": "Modern penny, good condition"}},
                                {{"name": "Brass Pot", "time_period": "Medieval (1000-1500 CE)", "country_of_origin": "Middle East or Europe", "additional_info": "Complete with lid, visible in center of image"}}
                            ]
                        }}"""
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Handle both direct array and wrapped in object
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'artifacts' in result:
                return result['artifacts']
            elif isinstance(result, dict):
                # If it's a dict with artifact keys, convert to list
                artifacts = []
                for key, value in result.items():
                    if isinstance(value, dict) and 'name' in value:
                        artifacts.append(value)
                    elif isinstance(value, list):
                        artifacts.extend(value)
                return artifacts if artifacts else []
            else:
                return []
        
        except Exception as e:
            print(f"Warning: Could not extract structured artifacts: {e}")
            # Fallback: try to parse basic info from analyses
            artifacts = []
            for analysis in all_analyses:
                analysis_lower = analysis.lower()
                if 'coin' in analysis_lower:
                    # Try to determine if modern or ancient
                    if 'penny' in analysis_lower or 'dime' in analysis_lower or 'modern' in analysis_lower:
                        time_period = 'Modern (2000-2024)'
                        country = 'United States'
                    else:
                        time_period = 'Unknown (possibly Ancient)'
                        country = 'Unknown'
                    artifacts.append({
                        'name': 'Coin',
                        'time_period': time_period,
                        'country_of_origin': country,
                        'additional_info': analysis[:100] + '...' if len(analysis) > 100 else analysis
                    })
                if 'pot' in analysis_lower or 'vessel' in analysis_lower:
                    artifacts.append({
                        'name': 'Brass Pot',
                        'time_period': 'Medieval to Modern (1000-1800 CE)',
                        'country_of_origin': 'Middle East or Europe',
                        'additional_info': analysis[:100] + '...' if len(analysis) > 100 else analysis
                    })
                if 'sword' in analysis_lower:
                    artifacts.append({
                        'name': 'Sword',
                        'time_period': 'Medieval to Ancient (500 BCE - 1500 CE)',
                        'country_of_origin': 'Europe or Middle East',
                        'additional_info': analysis[:100] + '...' if len(analysis) > 100 else analysis
                    })
                if 'bone' in analysis_lower:
                    artifacts.append({
                        'name': 'Bone',
                        'time_period': 'Unknown (Prehistoric to Modern)',
                        'country_of_origin': 'Unknown',
                        'additional_info': analysis[:100] + '...' if len(analysis) > 100 else analysis
                    })
                if 'drawing' in analysis_lower or 'carving' in analysis_lower:
                    artifacts.append({
                        'name': 'Stone Drawing',
                        'time_period': 'Prehistoric to Ancient (3000 BCE - 500 CE)',
                        'country_of_origin': 'Various (depends on style)',
                        'additional_info': analysis[:100] + '...' if len(analysis) > 100 else analysis
                    })
            return artifacts
    
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
            Tuple of (narration_text, jpg_image_paths, artifacts)
            - narration_text: The presentation script
            - jpg_image_paths: List of JPG image paths (for presentation)
            - artifacts: List of dictionaries with artifact information
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
            return ("Unable to analyze any images.", jpg_image_paths, [])
        
        # Extract structured artifact information
        artifacts = self.extract_artifacts(all_analyses)
        
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
            return (narration_text, jpg_image_paths, artifacts)
        
        except Exception as e:
            print(f"Error generating presentation script: {e}")
            # If AI fails, just combine the analyses
            narration_text = "\n\n".join(all_analyses)
            return (narration_text, jpg_image_paths, artifacts)

