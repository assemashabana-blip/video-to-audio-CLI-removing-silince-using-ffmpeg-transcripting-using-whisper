from flask import Flask, render_template, request, jsonify, send_file
from videoTOaudio import process_file
from yt_download import download
import whisper
import threading
import uuid
from pathlib import Path

app = Flask(__name__)
model = whisper.load_model("base")
jobs = {}


def generate_job_id():
    return "job_" + str(uuid.uuid4())


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    video_url = request.form["video_path"].strip()

    job_id = generate_job_id()
    jobs[job_id] = {"status": "Processing"}

    threading.Thread(target=run_job, args=(job_id, video_url, model)).start()
    return job_id


def run_job(job_id, video_url, model):
    try:
        audio_path = Path(download(video_url))
    except Exception as error:
        jobs[job_id] = {"status": "Failed", "error": f"Download failed: {error}"}
        return

    try:
        result = process_file(audio_path, model)
    except Exception as error:
        jobs[job_id] = {"status": "Failed", "error": str(error)}
        return

    if result is None:
        jobs[job_id] = {"status": "Failed", "error": "Transcription failed"}
    else:
        jobs[job_id] = {
            "status": "Done",
            "files": {
                "audio": str(audio_path),
                "transcript": str(result),
            },
        }




@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "unknown job"}), 404
    return jsonify(job)





@app.route("/download/<job_id>/<file_type>")
def download_file(job_id, file_type):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "unknown job"}), 404

    files = job.get("files")
    if files is None:
        return jsonify({"error": "job not finished"}), 404

    path = files.get(file_type)
    if path is None:
        return jsonify({"error": "unknown file type"}), 404

    return send_file(path, as_attachment=True)





if __name__ == "__main__":
    app.run(debug=True)