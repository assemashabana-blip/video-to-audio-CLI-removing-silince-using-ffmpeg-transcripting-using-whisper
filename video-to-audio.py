import subprocess
import argparse
import sys
from pathlib import Path
def main():
    parser = argparse.ArgumentParser(description="Convert video to audio.")
    parser.add_argument("video", help="Path to the input video file")
    args = parser.parse_args()
    file_validation(args.video)
    output_audio=renaming_the_file(args.video)
    running_ffempeg(args.video, output_audio)

    


def file_validation(filename):
    if not filename.lower().endswith((".mp4", ".mkv", ".avi", ".webm", ".flv", ".ts")):
        print(f"Unsupported format: {filename}", file=sys.stderr)
        sys.exit(1)

    if not Path(filename).is_file():
        print(f"File not found: {filename}", file=sys.stderr)
        sys.exit(1)


def renaming_the_file(filename):
    output_audio = Path(filename).with_suffix(".mp3")
    return output_audio


def running_ffempeg(filename,output_audio):
    try:
        subprocess.run(["ffmpeg", "-i", filename, "-vn", "-acodec", "libmp3lame", str(output_audio)], check=True)
    except subprocess.CalledProcessError:
        print(f"Conversion failed: {filename}", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main()



    
        
    

