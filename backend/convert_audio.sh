#!/bin/bash
# Script to convert Teams MP4 recordings to WAV for transcription
# Usage: ./convert_audio.sh input.mp4 output.wav

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input.mp4 output.wav"
    echo "Example: $0 teams_recording.mp4 audio.wav"
    exit 1
fi

INPUT="$1"
OUTPUT="$2"

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed"
    echo ""
    echo "To install ffmpeg on Mac:"
    echo "  brew install ffmpeg"
    echo ""
    echo "Or download from: https://ffmpeg.org/download.html"
    exit 1
fi

echo "Converting $INPUT to $OUTPUT..."
echo "Extracting audio at 16kHz (optimized for speech recognition)..."

ffmpeg -i "$INPUT" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Conversion successful!"
    echo "Output file: $OUTPUT"
    echo ""
    echo "You can now test with:"
    echo "  python test_audio_simple.py $OUTPUT"
else
    echo ""
    echo "✗ Conversion failed"
    exit 1
fi
