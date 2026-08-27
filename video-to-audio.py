import subprocess
import whisper
import argparse
import sys
import textwrap
from pathlib import Path

MEDIA_EXTENSIONS = (".mp4", ".mkv", ".avi", ".webm", ".flv", ".ts", ".mp3", ".m4a")
SILENCE_FILTER = "silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-20dB"


def main():
    parser = argparse.ArgumentParser(description="Convert video to audio and transcribe.")
    parser.add_argument("video", help="Path to the input video file or a directory of videos")
    args = parser.parse_args()

    target = Path(args.video)
    files_to_convert = []

    if target.is_dir():
        for file in target.iterdir():
            if file.suffix.lower() in MEDIA_EXTENSIONS:
                files_to_convert.append(file)
    elif target.is_file():
        files_to_convert.append(target)
    else:
        print(f"Path not found: {target}", file=sys.stderr)
        sys.exit(1)

    if not files_to_convert:
        print("No media files to convert.", file=sys.stderr)
        sys.exit(1)

    success_count = 0
    fail_count = 0
    cleaned_files = []

    for file in files_to_convert:
        if not file_validation(file):
            fail_count += 1
            continue

        raw_audio = output_path(file)
        clean_audio = output_path(file, "_clean")

        if not running_ffmpeg(file, raw_audio):
            fail_count += 1
            continue

        if not remove_audio_silence(raw_audio, clean_audio):
            fail_count += 1
            continue

        cleaned_files.append((file, clean_audio))
        success_count += 1

    if cleaned_files:
        print("Loading Whisper model...")
        model = whisper.load_model("base")

        for original, cleaned in cleaned_files:
            if not transcribe(model, original, cleaned):
                fail_count += 1

    print(f"Done: {success_count} succeeded, {fail_count} failed")
    if fail_count > 0:
        sys.exit(1)


def file_validation(filename):
    filename = Path(filename)

    if filename.suffix.lower() not in MEDIA_EXTENSIONS:
        print(f"Unsupported format: {filename}", file=sys.stderr)
        return False

    if not filename.is_file():
        print(f"File not found: {filename}", file=sys.stderr)
        return False

    return True


def output_path(filename, suffix="", extension=".mp3"):
    filename = Path(filename)
    folder = filename.parent / filename.stem
    folder.mkdir(exist_ok=True)
    return folder / (filename.stem + suffix + extension)


def running_ffmpeg(filename, raw_audio):
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(filename), "-vn",
             "-acodec", "libmp3lame", "-b:a", "192k", str(raw_audio)],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        print(f"Conversion failed: {filename}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ffmpeg not found. Install it and make sure it's on your PATH.", file=sys.stderr)
        return False


def remove_audio_silence(raw_audio, clean_audio):
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_audio), "-af", SILENCE_FILTER,
             "-b:a", "192k", str(clean_audio)],
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        print(f"Silence removal failed: {raw_audio}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ffmpeg not found. Install it and make sure it's on your PATH.", file=sys.stderr)
        return False


def transcribe(model, original, cleaned):
    transcript_path = output_path(original, extension=".txt")
    try:
        result = model.transcribe(str(cleaned), fp16=False)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(textwrap.fill(result["text"], width=70))
        print(f"Transcript saved: {transcript_path}")
        return True
    except Exception as error:
        print(f"Transcription failed for {cleaned}: {error}", file=sys.stderr)
        return False




if __name__ == "__main__":
    main()