# Archaeological Site AI Agent

An AI program for FLL competition that looks at drone photos and creates presentations!

## What It Does

1. 📥 Gets photos from Google Drive
2. 👁️ Uses AI to find artifacts (coins, pottery, swords, bones, etc.)
3. ✍️ Writes a presentation script
4. 🔊 Creates audio narration (30-40 seconds)
5. 🎨 Makes a web page with photos and audio

## Quick Start

### 1. Install Requirements

```bash
pip3 install -r requirements.txt
```

### 2. Set Up Google Drive

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable **Google Drive API**
4. Create OAuth 2.0 credentials (Desktop app)
5. Download and save as `credentials.json` in this folder

### 3. Set Up OpenAI API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Get your key from: https://platform.openai.com/api-keys

### 4. Run the Program

```bash
python3 main.py 3
```

This downloads and analyzes the 3 most recent images from Google Drive.

**Options:**
- `python3 main.py 5` - Analyze 5 images
- `python3 main.py 3 --openai-key sk-...` - Use different API key

## Output

The program creates:
- **Audio file**: `archaeological_narration_YYYYMMDD_HHMMSS.mp3`
- **Presentation**: `presentation_YYYYMMDD_HHMMSS.html` (opens in browser automatically!)

## How It Works (Simple Version)

```
main.py → Downloads images → AI analyzes → Creates audio → Makes presentation
```

The code is split into modules:
- `google_drive.py` - Downloads photos
- `image_analyzer.py` - AI looks at photos
- `audio_generator.py` - Makes audio from text
- `presentation.py` - Creates web page

Each module does one job, making it easy to understand!

## Project Structure

```
innovation/
├── main.py                    # Run this!
├── archaeological_agent/      # All the modules
│   ├── config.py              # Settings
│   ├── google_drive.py        # Downloads from Google Drive
│   ├── image_converter.py     # Converts images to JPG
│   ├── image_analyzer.py     # AI analysis
│   ├── audio_generator.py     # Text-to-speech
│   └── presentation.py        # HTML presentation
└── requirements.txt           # Python packages needed
```

## Troubleshooting

**"credentials.json not found"**
- Make sure you downloaded it from Google Cloud Console

**"OpenAI API key not found"**
- Set it: `export OPENAI_API_KEY='your-key'`

**"No images downloaded"**
- Check you have access to the Google Drive folder
- Make sure the folder ID is correct

**Images won't convert (HEIC files)**
- The program tries multiple methods automatically
- If it fails, manually convert HEIC to JPG first

## For FLL Competition

This project shows:
- ✅ AI Integration - Using vision AI to analyze images
- ✅ Automation - Automatic download and processing
- ✅ Real-world Application - Practical archaeology use case
- ✅ Clean Code - Easy to understand and modify!

The narration is designed for 7th graders presenting to teachers - clear, confident, and educational!

## License

Created for FLL competition purposes.
