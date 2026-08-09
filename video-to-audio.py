import subprocess
import argparse
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description="Convert video to audio.")
parser.add_argument("video", help="Path to the input video file")
args = parser.parse_args()
filename = args.video


if not filename.lower().endswith((".mp4", ".mkv", ".avi", ".webm", ".flv", ".ts")):
    print(f"Unsupported format: {filename}", file=sys.stderr)
    sys.exit(1)

if not Path(filename).is_file():
    print(f"File not found: {filename}", file=sys.stderr)
    sys.exit(1)


output_audio = Path(filename).with_suffix(".mp3")
print(output_audio)

    
        
    

