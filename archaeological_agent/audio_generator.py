"""
Audio Generator Module

This module converts text to speech (TTS).
It creates an audio file from the presentation script.
"""

import os
from typing import Optional

try:
    from gtts import gTTS
except ImportError:
    print("Error: gTTS library not installed.")
    print("Run: pip3 install gtts")
    # Will use fallback if available
    gTTS = None


class AudioGenerator:
    """
    Generates audio from text using text-to-speech.
    
    This class takes the presentation script and converts it
    into an audio file (MP3) that can be played.
    """
    
    def text_to_speech(self, text: str, output_path: str, 
                      lang: str = 'en', slow: bool = False) -> bool:
        """
        Convert text to speech and save as audio file.
        
        This function:
        1. Takes the presentation script text
        2. Uses Google Text-to-Speech to create audio
        3. Saves it as an MP3 file
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the audio file
            lang: Language code (default: 'en' for English)
            slow: Whether to speak slowly (default: False)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not gTTS:
                print("Error: gTTS not available. Install with: pip3 install gtts")
                return False
            
            print(f"\nGenerating audio narration...")
            
            # Make sure text isn't too long (TTS has limits)
            max_length = 5000
            if len(text) > max_length:
                print(f"Warning: Text is long ({len(text)} chars), truncating...")
                text = text[:max_length] + "..."
            
            # Create the audio file
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(output_path)
            print(f"✓ Audio saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False

