import threading
import time
import subprocess
from fastapi import FastAPI, UploadFile, File
import uvicorn
import sys
import random
from fastapi.responses import JSONResponse
import tempfile
import os

# Define a simple FastAPI app (demo model)
app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello from the demo model via Tunnelmole!"}

@app.post("/process-video")
async def process_video_endpoint(video: UploadFile = File(...)):
    """
    Endpoint that processes a video file and returns analysis results
    
    Args:
        video: The uploaded video file
        
    Returns:
        dict: Analysis results with scores for different skills
    """
    # Create a temporary file to store the uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        # Write the uploaded file to the temporary file
        temp_file.write(await video.read())
        temp_file_path = temp_file.name
    
    try:
        # Simulate processing time (in a real app, this would call your actual video processing code)
        time.sleep(3)
        
        # Generate random scores for demonstration
        jump_score = random.randint(3, 5)
        running_score = random.randint(2, 5)
        passing_score = random.randint(2, 5)
        
        # Calculate overall score
        overall_score = (jump_score + running_score + passing_score) / 3
        
        # Compile results
        results = {
            "jump_score": jump_score,
            "running_score": running_score,
            "passing_score": passing_score,
            "overall_score": overall_score,
            "processing_time": random.uniform(2.5, 5.0)
        }
        
        return JSONResponse(content=results)
    
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

# Function to install dependencies
def install_dependencies():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "python-multipart"])
    subprocess.check_call(["npm", "install", "-g", "tunnelmole"])

# Function to run the FastAPI server
def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# Function to run Tunnelmole on port 8000
def run_tunnelmole():
    subprocess.run(["tmole", "8000"])

# Install dependencies first
install_dependencies()

# Start the FastAPI server in a background thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait a few seconds to ensure the server is up
time.sleep(3)

# Start Tunnelmole in a background thread so the Colab cell doesn't block
tunnel_thread = threading.Thread(target=run_tunnelmole, daemon=True)
tunnel_thread.start()

print("FastAPI server is running on port 8000. Check the cell output for Tunnelmole's public URL.")
