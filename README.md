# آساطير الغد (Legends of Tomorrow) - Soccer Skills Analyzer

A Streamlit web application that analyzes soccer skills from video uploads using computer vision and machine learning.

## Features

- Upload soccer video files (mp4, mov, avi)
- Analyze three key soccer skills:
  - Jumping with ball
  - Running with ball
  - Passing
- Get an overall score and detailed breakdown
- Download results as JSON

## Requirements

- Python 3.8+
- Streamlit
- OpenCV
- NumPy
- PyTorch
- Ultralytics (YOLOv8)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## How It Works

The application uses two YOLOv8 models:
- **YOLO pose model** to detect body keypoints
- **YOLO object detection model** to identify soccer balls

When a video is uploaded, the application:
1. Saves the video to a temporary file
2. Processes it with the video_processor module
3. Detects and scores the soccer skills
4. Displays the results in a user-friendly interface

## Skills Analysis

### Jumping with Ball
Detects knee contact with the ball and evaluates the skill based on the number of successful contacts.

### Running with Ball
Evaluates how well the player maintains control of the ball while running at speed.

### Passing
Analyzes passing attempts and successful passes based on ball movement and player positioning.

## File Structure

- `app.py` - Main Streamlit application
- `video_processor.py` - Core video processing and analysis module
- `requirements.txt` - Required Python dependencies

## License

[MIT License](LICENSE)

## Credits

Created for the آساطير الغد (Legends of Tomorrow) Project. 