# Video to Audio Transcriber

A command-line tool that takes a video file (or a whole folder of them), extracts
the audio, strips out long silences, and produces a text transcript using OpenAI's
Whisper.

## What it produces

For an input file `lecture.mp4`, the tool creates a folder next to it:

```
lecture/
  lecture.mp3         # extracted audio, 192 kbps
  lecture_clean.mp3   # same audio with long silences removed
  lecture.txt         # transcript, wrapped at 70 characters
```

## Requirements

- **Python 3.8+**
- **ffmpeg** installed and available on your PATH. Check with `ffmpeg -version`.
  If that command isn't recognised, ffmpeg is either not installed or the folder
  containing it isn't on PATH.
- **openai-whisper**:
  ```
  pip install openai-whisper
  ```
  The first run downloads the `base` model (~140 MB). This happens once.

## Usage

Convert a single file:

```
python extract.py lecture.mp4
```

Convert every video in a folder:

```
python extract.py ./recordings
```

Supported input formats: `.mp4`, `.mkv`, `.avi`, `.webm`, `.flv`, `.ts`, `.mp3`, `.m4a`

## How it works

Each file goes through three stages. If any stage fails, that file is counted as a
failure and the tool moves on to the next one — one bad file does not stop the batch.

1. **Extract** — ffmpeg pulls the audio track out of the video and encodes it as
   MP3 at 192 kbps.
2. **Clean** — ffmpeg's `silenceremove` filter cuts out silences longer than one
   second.
3. **Transcribe** — Whisper reads the cleaned audio and writes the text.

At the end the tool prints a summary (`Done: N succeeded, N failed`) and exits with
a non-zero code if anything failed, so it can be used in scripts.

## Notes and design decisions

**Silence threshold is -29dB.** This was measured, not guessed. Running ffmpeg's
`silencedetect` filter against a real 26-minute lecture at -50dB found almost
nothing — the recording's noise floor (room tone, mic hiss) never dropped that low.
At -29dB it found roughly 27 seconds of silence across 26 intervals, and the actual
cleaned file came out about 30 seconds shorter. To re-measure on different audio:

```
ffmpeg -i input.mp3 -af silencedetect=noise=-30dB:d=1 -f null -
```

This only reports; it writes no file. Adjust the `noise` value and `d` (minimum
silence duration in seconds) and watch how the results change.

**Savings are modest.** About 2% on typical lecture audio. Lowering `stop_duration`
below 1 second would cut more but makes the audio sound clipped and unnatural.

**Both encodes use an explicit 192 kbps bitrate.** Without this, ffmpeg picks
different defaults for the two passes, and the output files end up different sizes
for reasons that have nothing to do with silence removal — which makes it impossible
to tell whether the filter did anything.

**Whisper loads once per run**, not once per file, and only if there is at least one
file to transcribe. Loading the model is slow, so it happens after all conversions
are done rather than at startup.

**Both ffmpeg calls use `-y`.** Without it, ffmpeg prompts before overwriting an
existing file — and since it runs as a subprocess, that prompt is invisible and the
program appears to hang forever.

## Possible next steps

- A `--no-clean` flag to skip silence removal and transcribe the raw audio
- Configurable Whisper model size (`tiny`, `base`, `small`, `medium`)
- Timestamped transcripts using Whisper's segment output
- Recursive folder scanning for nested directories