"""
Presentation Module

This module creates an HTML presentation that shows images
with synchronized audio narration. Perfect for FLL presentations!
"""

import os
import json
import base64
from pathlib import Path
from typing import List, Optional


def create_presentation(image_paths: List[str], audio_path: str, 
                       output_path: str = 'presentation.html') -> Optional[str]:
    """
    Create an HTML presentation with images and audio.
    
    This function creates a web page that:
    - Shows all the images in a slideshow
    - Plays the audio narration
    - Lets you navigate between images
    - Is perfect for presentations!
    
    Args:
        image_paths: List of paths to image files (should be JPG)
        audio_path: Path to the audio narration file
        output_path: Where to save the HTML file
        
    Returns:
        Path to the created HTML file, or None if it failed
    """
    # Convert images to base64 (so they're embedded in the HTML)
    image_data_list = []
    for img_path in image_paths:
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                ext = Path(img_path).suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')
                
                image_data_list.append({
                    'data': img_data,
                    'mime': mime_type,
                    'name': Path(img_path).name
                })
    
    # Get audio data
    audio_data = None
    audio_mime = 'audio/mpeg'
    if os.path.exists(audio_path):
        with open(audio_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')
        ext = Path(audio_path).suffix.lower()
        audio_mime = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.ogg': 'audio/ogg'
        }.get(ext, 'audio/mpeg')
    else:
        print(f"Warning: Audio file not found: {audio_path}")
        print("  Presentation will be created without audio")
    
    # Create the HTML file
    images_json = json.dumps(image_data_list)
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FLL Archaeological Discovery</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow: hidden;
            height: 100vh;
        }}
        .container {{
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .title {{
            color: white;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .image-container {{
            width: 90%;
            max-width: 1200px;
            height: 70vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 10px;
        }}
        .image-info {{
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .controls {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            margin-top: 20px;
        }}
        .btn {{
            background: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .audio-player {{
            margin-top: 15px;
        }}
        .audio-player audio {{
            width: 400px;
            height: 50px;
            border-radius: 25px;
        }}
        .slide-counter {{
            color: white;
            font-size: 1.2em;
            margin-top: 15px;
        }}
        .fade-in {{
            animation: fadeIn 0.5s;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Archaeological Discovery Project</h1>
        <div class="image-container" id="imageContainer">
            <img id="currentImage" src="" alt="Archaeological site image">
            <div class="image-info" id="imageInfo"></div>
        </div>
        <div class="controls">
            <button class="btn" onclick="previousImage()">← Previous</button>
            <button class="btn" onclick="playPauseAudio()" id="playBtn">▶ Play</button>
            <button class="btn" onclick="nextImage()">Next →</button>
        </div>
        <div class="audio-player">
            <audio id="audioPlayer" controls>
                <source src="data:{audio_mime};base64,{audio_data if audio_data else ''}" type="{audio_mime}">
            </audio>
        </div>
        <div class="slide-counter">
            <span id="currentSlide">1</span> / <span id="totalSlides">{len(image_data_list)}</span>
        </div>
    </div>
    <script>
        // Image data (all images embedded in the HTML)
        const images = {images_json};
        let currentIndex = 0;
        const audioPlayer = document.getElementById('audioPlayer');
        
        // Show an image
        function showImage(index) {{
            if (index < 0 || index >= images.length) return;
            currentIndex = index;
            document.getElementById('currentImage').src = `data:${{images[index].mime}};base64,${{images[index].data}}`;
            document.getElementById('imageInfo').textContent = images[index].name;
            document.getElementById('currentSlide').textContent = index + 1;
            document.getElementById('imageContainer').classList.add('fade-in');
        }}
        
        // Navigation functions
        function nextImage() {{ 
            if (currentIndex < images.length - 1) showImage(currentIndex + 1); 
        }}
        function previousImage() {{ 
            if (currentIndex > 0) showImage(currentIndex - 1); 
        }}
        function playPauseAudio() {{
            if (audioPlayer.paused) {{
                audioPlayer.play();
                document.getElementById('playBtn').textContent = '⏸ Pause';
            }} else {{
                audioPlayer.pause();
                document.getElementById('playBtn').textContent = '▶ Play';
            }}
        }}
        
        // Keyboard controls (arrow keys to navigate, Enter to play/pause)
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') nextImage();
            else if (e.key === 'ArrowLeft') previousImage();
            else if (e.key === 'Enter') playPauseAudio();
        }});
        
        // When page loads, show first image
        window.addEventListener('load', () => {{
            showImage(0);
        }});
    </script>
</body>
</html>'''
    
    # Save the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Created presentation: {output_path}")
    return output_path


def open_in_browser(presentation_path: str):
    """
    Open the presentation HTML file in the default web browser.
    
    Args:
        presentation_path: Path to the HTML file
    """
    try:
        import webbrowser
        file_url = f"file://{os.path.abspath(presentation_path)}"
        webbrowser.open(file_url)
        print(f"✓ Opened presentation in browser")
    except Exception as e:
        print(f"⚠ Could not open browser automatically: {e}")
        print(f"   Please open manually: {os.path.abspath(presentation_path)}")

