# Install necessary packages

# Import required libraries
from fastapi import FastAPI, File, UploadFile
import uvicorn
import cv2
import torch
import os
import threading
from pyngrok import ngrok

# Create the FastAPI app
app = FastAPI()

# Load the YOLOv5 model from torch hub (this will download the model if not available)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.conf = 0.5  # Optional: adjust confidence threshold

def analyze_video(video_path):
    """
    Process the video frame by frame and return a summary of detections per frame.
    """
    cap = cv2.VideoCapture(video_path)
    results_summary = []
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Run YOLO inference on the frame
        results = model(frame)
        # Extract detections (results.xyxy[0] contains detections in the current frame)
        detections = results.xyxy[0].numpy()
        count = len(detections)  # number of detections in the frame
        results_summary.append({'frame': frame_idx, 'detections': int(count)})
        frame_idx += 1

    cap.release()
    return results_summary

@app.post("/analyze_video")
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """
    API endpoint to accept a video file, process it using YOLO, and return detection results.
    """
    # Save the uploaded file to a temporary location
    file_location = "temp_video.mp4"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Analyze the video and get the summary results
    analysis_results = analyze_video(file_location)
    
    # Remove the temporary file
    os.remove(file_location)
    
    return {"analysis": analysis_results}

# Function to run the server using Uvicorn
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Open an ngrok tunnel to the local server
public_url = ngrok.connect(8000).public_url
print("Public URL:", public_url)

# Run the server in a background thread so that the Colab cell doesn't block
server_thread = threading.Thread(target=run_server)
server_thread.start()
