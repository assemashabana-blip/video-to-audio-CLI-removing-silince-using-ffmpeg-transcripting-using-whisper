import whisper
import sys
import textwrap
from pathlib import Path
from yt_download import download

AUDIO_EXTENSIONS = (".mp3", ".m4a", ".wav", ".webm")


def main():
    if len(sys.argv) < 2:
        print("Error: Missing YouTube URL.", file=sys.stderr)
        print("Usage: python videoTOaudio.py <YOUTUBE_URL>", file=sys.stderr)
        sys.exit(1)

    video_url = sys.argv[1]

    try:
        target = Path(download(video_url))
    except Exception as error:
        print(f"Download failed: {error}", file=sys.stderr)
        sys.exit(1)

    print("Loading Whisper model...")
    model = whisper.load_model("base")

    if process_file(target, model):
        print("Done: 1 succeeded, 0 failed")
    else:
        print("Done: 0 succeeded, 1 failed")
        sys.exit(1)


def file_validation(target):
    if target.suffix.lower() not in AUDIO_EXTENSIONS:
        print(f"Unsupported format: {target}", file=sys.stderr)
        return False

    if not target.is_file():
        print(f"File not found: {target}", file=sys.stderr)
        return False

    return True


def transcribe(model, target, transcript_path):
    try:
        result = model.transcribe(str(target), fp16=False)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(textwrap.fill(result["text"], width=70))
        print(f"Transcript saved: {transcript_path}")
        return True
    except Exception as error:
        print(f"Transcription failed for {target}: {error}", file=sys.stderr)
        return False


def process_file(target, model):
    if not file_validation(target):
        return None

    transcript = target.with_suffix(".txt")

    if not transcribe(model, target, transcript):
        return None

    return transcript


if __name__ == "__main__":
    main()