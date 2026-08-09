import subprocess
import argparse
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description="Convert video to audio.")
parser.add_argument("video", help="Path to the input video file")
args = parser.parse_args()
filename = args.video

try:
    if filename.lower().endswith(".mp4",".mkv",".avi",".webm",".flv",".ts"):
        pass
    else:
        raise(TypeError)
    if not Path(filename).is_file():
        print(f"File not found: {filename}")
        sys.exit(1)

        
except TypeError:
    print("Not a valid Format")

    
        
    

