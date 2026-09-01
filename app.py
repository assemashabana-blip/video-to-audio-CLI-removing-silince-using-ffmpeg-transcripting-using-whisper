from flask import Flask , render_template,request,jsonify
from videoTOaudio import process_file
import whisper
import threading
import uuid
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
    job_id = generate_job_id()
    jobs[job_id] = {"status": "Processing"}
    video_path = request.form["video_path"].strip().strip('"')
    threading.Thread(target=run_job, args=(job_id, video_path, model)).start()
    return job_id 




def run_job(job_id, video_path, model):
    try:
        result = process_file(video_path, model)
    except Exception as error:
        jobs[job_id] = {"status": "Failed","error":str(error)}
        return

    if result is None:
        jobs[job_id] = {"status": "Failed","error":"processing failed"}
    else:
        raw_audio, clean_audio, transcript = result
        jobs[job_id] = {
            "status": "Done",
            "files": {
                "raw_audio": str(raw_audio),
                "clean_audio": str(clean_audio),
                "transcript": str(transcript),
            },
        }



@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
              
    if job is None:
        return jsonify({"error": "unknown job"}), 404
    return jsonify(job)

        




if __name__ == "__main__":
    app.run(debug=True)

