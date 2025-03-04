from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import subprocess
import shutil
import os
import uuid

app = FastAPI()

UPLOAD_DIR = "./uploads"
OUTPUT_DIR = "./outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_inference(audio_path: str, output_filename: str):
    """
    Runs inference on the given audio file and stores the output video.
    """
    output_video_path = os.path.join(OUTPUT_DIR, output_filename)

    inference_cmd = [
        "python3", "main.py", "data/May",
        "--workspace", "model/trial_may",
        "-O", "--test", "--test_train",
        "--asr_model", "ave", "--portrait",
        "--aud", audio_path
    ]

    process = subprocess.run(inference_cmd, capture_output=True, text=True)
    
    if os.path.exists(output_video_path):
        return output_video_path
    else:
        return None

@app.post("/predict/")
async def predict(background_tasks: BackgroundTasks, audio: UploadFile = File(...)):
    """
    Accepts an audio file, runs inference in the background, and returns the output.
    """
    # Generate unique filename
    file_ext = os.path.splitext(audio.filename)[-1]
    unique_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"input_{unique_id}{file_ext}")
    output_filename = f"output_{unique_id}.mp4"

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # Run inference in the background
    background_tasks.add_task(run_inference, file_path, output_filename)

    return JSONResponse(content={"message": "Inference started", "output_file": f"/output/{output_filename}"})

@app.get("/output/{filename}")
async def get_output(filename: str):
    """
    Serves the generated video file.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=filename)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
