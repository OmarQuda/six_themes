# Install necessary packages

import os
import time
import threading
import subprocess
import cv2
import torch
import uvicorn
from fastapi import FastAPI, File, UploadFile

# Create the FastAPI app
app = FastAPI()

# Load the YOLOv5 model from torch hub (this downloads the model if not cached)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = 0.5  # Adjust confidence threshold if needed

def analyze_video(video_path):
    """
    Process the video frame by frame using YOLO and return a summary list with
    the frame index and count of detections.
    """
    cap = cv2.VideoCapture(video_path)
    results_summary = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Perform inference on the frame
        results = model(frame)
        # results.xyxy[0] contains detection boxes; count them
        detections = results.xyxy[0].numpy()
        count = len(detections)
        results_summary.append({'frame': frame_idx, 'detections': int(count)})
        frame_idx += 1

    cap.release()
    return results_summary

@app.post("/analyze_video")
async def analyze_video_endpoint(file: UploadFile = File(...)):
       # Save the uploaded file to a temporary location
    file_location = "temp_video.mp4"
    with open(file_location, "wb") as f:
        f.write(await file.read())
       
       # Process the video
    analysis_results = analyze_video(file_location)
       
       # Clean up the temporary file
    os.remove(file_location)
       
       # Return the results
    return {"analysis": analysis_results}

def run_server():
    """Run the FastAPI app using Uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_localtunnel():
    """
    Run LocalTunnel to expose port 8000. The public URL will be printed in the output.
    Note: This command will run and print logs directly.
    """
    subprocess.run(["lt", "--port", "8000"])

# Start the FastAPI server in a background thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait briefly to ensure the server has started
time.sleep(3)

# Start LocalTunnel in a separate background thread
lt_thread = threading.Thread(target=run_localtunnel, daemon=True)
lt_thread.start()

print("The FastAPI server is running on port 8000, and LocalTunnel is establishing a public URL. Check the output logs for the public URL.")
