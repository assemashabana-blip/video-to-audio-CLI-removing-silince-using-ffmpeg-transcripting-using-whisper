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

    success_count = 0
    fail_count = 0
    

    for file in files_to_convert:
        if not file_validation(file):
            fail_count += 1
            continue

        output_audio = output_path(file)
        if running_ffmpeg(file, output_audio):
            success_count += 1
        else:
            fail_count += 1

    print(f"Done: {success_count} succeeded, {fail_count} failed")
    if fail_count > 0:
        sys.exit(1)


def file_validation(filename):
    filename = Path(filename)

    if filename.suffix.lower() not in VIDEO_EXTENSIONS:
        print(f"Unsupported format: {filename}", file=sys.stderr)
        return False

    if not filename.is_file():
        print(f"File not found: {filename}", file=sys.stderr)
        return False
    

    return True


def output_path(filename):
    filename = Path(filename)
    folder = filename.parent / filename.stem
    folder.mkdir(exist_ok=True)
    return folder / (filename.stem + ".mp3")


def running_ffmpeg(filename, output_audio):
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(filename), "-vn", "-acodec", "libmp3lame", str(output_audio)],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        print(f"Conversion failed: {filename}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ffmpeg not found. Install it and make sure it's on your PATH.", file=sys.stderr)
        return False


if __name__ == "__main__":
    main()

