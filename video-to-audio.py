import subprocess
import argparse
import sys
from pathlib import Path

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".webm", ".flv", ".ts")


def main():
    parser = argparse.ArgumentParser(description="Convert video to audio.")
    parser.add_argument("video", help="Path to the input video file or a directory of videos")
    args = parser.parse_args()

    target = Path(args.video)
    files_to_convert = []

    if target.is_dir():
        for file in target.iterdir():
            if file.suffix.lower() in VIDEO_EXTENSIONS:
                files_to_convert.append(file)
    elif target.is_file():
        files_to_convert.append(target)
    else:
        print(f"Path not found: {target}", file=sys.stderr)
        sys.exit(1)

    if not files_to_convert:
        print("No video files to convert.", file=sys.stderr)
        sys.exit(1)

    if not file_validation(files_to_convert):
        sys.exit(1)

    # Loop over every file, not just args.video
    for file in files_to_convert:
        output_audio = output_path(file)
        running_ffmpeg(file, output_audio)


def file_validation(files_to_convert):
    for filename in files_to_convert:
        filename = Path(filename)

        if filename.suffix.lower() not in VIDEO_EXTENSIONS:
            print(f"Unsupported format: {filename}", file=sys.stderr)
            return False

        if not filename.is_file():
            print(f"File not found: {filename}", file=sys.stderr)
            return False

    # return True only after checking ALL files, not just the first one
    return True


def output_path(filename):
    return Path(filename).with_suffix(".mp3")


def running_ffmpeg(filename, output_audio):
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(filename), "-vn", "-acodec", "libmp3lame", str(output_audio)],
            check=True,
        )
    except subprocess.CalledProcessError:
        print(f"Conversion failed: {filename}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ffmpeg not found. Install it and make sure it's on your PATH.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()



    
        
    

