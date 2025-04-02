import streamlit as st
import tempfile
import os
import time
import json
import random
import requests
from pathlib import Path

# Define a function to call the FastAPI endpoint running in Colab
def process_video_api(video_path, api_endpoint=None):
    """
    Process a video by sending it to the FastAPI endpoint running in Google Colab
    
    Args:
        video_path (str): Path to the video file
        api_endpoint (str): URL of the FastAPI endpoint
        
    Returns:
        dict: Results and scores from the video analysis
    """
    # If no API endpoint is provided, use the mock processor
    if not api_endpoint:
        return mock_process_video(video_path)
    
    try:
        # Open the video file in binary mode
        with open(video_path, 'rb') as video_file:
            # Create a files dictionary for the request
            files = {'file': (os.path.basename(video_path), video_file, 'video/mp4')}
            
            # Send the POST request to the API
            response = requests.post(api_endpoint, files=files)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Get the analysis results
                api_response = response.json()
                
                # Process the API response to match our expected format
                # We'll convert the detections into skill scores for this demo
                raw_analysis = api_response.get('analysis', [])
                
                # Calculate averages of detections per frame to create skill scores
                detection_counts = [frame['detections'] for frame in raw_analysis]
                if detection_counts:
                    avg_detections = sum(detection_counts) / len(detection_counts)
                    max_detections = max(detection_counts) if detection_counts else 0
                    
                    # Map the detection counts to skill scores
                    jump_score = min(5, int(max_detections / 2))
                    running_score = min(5, int(avg_detections))
                    passing_score = min(5, int(max_detections / 3))
                    
                    # Calculate overall score
                    overall_score = (jump_score + running_score + passing_score) / 3
                else:
                    jump_score = running_score = passing_score = overall_score = 0
                
                # Return formatted results
                return {
                    "jump_score": jump_score,
                    "running_score": running_score,
                    "passing_score": passing_score,
                    "overall_score": overall_score,
                    "processing_time": response.elapsed.total_seconds(),
                    "raw_analysis": raw_analysis
                }
            else:
                # If the request failed, raise an exception
                response.raise_for_status()
    except Exception as e:
        st.error(f"Error communicating with the API: {str(e)}")
        # Fallback to mock processor if API fails
        return mock_process_video(video_path)

# Rename the original mock function
def mock_process_video(video_path):
    """
    Mock implementation of video processing to use as fallback when API is unavailable
    
    Args:
        video_path (str): Path to the input video
        
    Returns:
        dict: Mock results and scores for different skills
    """
    # Simulate processing time
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
    
    return results

# Define function alias - this is the main function that will be called
def process_video(video_path):
    """
    Process a video by sending it to the API endpoint or using the mock processor as fallback
    
    Args:
        video_path (str): Path to the input video
        
    Returns:
        dict: Results and scores from the video analysis
    """
    # Get the API endpoint from session state or Streamlit secrets
    api_endpoint = st.session_state.get('api_endpoint', None)
    return process_video_api(video_path, api_endpoint)

# Define theme colors - Clean navy and purple palette
NAVY_COLOR = "#1A237E"       # Dark navy for primary elements
NAVY_LIGHT = "#303F9F"       # Lighter navy for secondary elements
PURPLE_COLOR = "#6F00FF"     # Purple accent color  
PURPLE_LIGHT = "#9575CD"     # Lighter purple for highlighting
DARK_BG_COLOR = "#0B0D17"    # Very dark navy for backgrounds
WHITE_TEXT = "#FFFFFF"       # White for text on dark backgrounds
DARK_TEXT = "#212121"        # Dark text color for light backgrounds
LIGHT_BG = "#F5F5F7"         # Light background for containers
BG_COLOR = "#EFEFF5"         # Main app background color

# Set page config
st.set_page_config(
    page_title="آساطير الغد - Soccer Skills Analyzer",
    page_icon="⚽",
    layout="wide",
)

def local_css():
    """Apply custom CSS for styling with navy and purple theme"""
    st.markdown(
        f"""
        <style>
        /* Base Layout */
        .main {{
            background-color: {BG_COLOR};
        }}
        
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            background-color: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-top: 1rem;
        }}
        
        /* Improved Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: {NAVY_COLOR};
            margin-bottom: 1.2rem;
            font-weight: 600;
        }}
        
        p {{
            margin-bottom: 1rem;
            line-height: 1.6;
        }}
        
        /* Interactive Elements */
        .stProgress > div > div {{
            background-color: {PURPLE_COLOR};
            height: 8px;
            border-radius: 4px;
        }}
        
        .stProgress {{
            margin-top: 0.5rem;
            margin-bottom: 2rem;
        }}
        
        /* File Upload */
        .uploadedFiles {{
            background-color: {LIGHT_BG};
            border: 1px solid {NAVY_LIGHT};
            border-radius: 6px;
            padding: 1rem;
        }}
        
        /* Buttons */
        .stButton button {{
            background-color: {PURPLE_COLOR};
            color: white;
            font-weight: 600;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            border: none;
            transition: all 0.2s ease;
        }}
        
        .stButton button:hover {{
            background-color: {NAVY_COLOR};
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        /* Sidebar */
        .sidebar .sidebar-content {{
            background-color: {NAVY_LIGHT};
            color: {WHITE_TEXT};
        }}
        
        /* Section Headings */
        .heading-container {{
            background-color: {DARK_BG_COLOR};
            padding: 1.2rem;
            border-radius: 10px;
            margin-bottom: 2.5rem;
            margin-top: 2rem;
            display: flex;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .heading-number {{
            background-color: {PURPLE_COLOR};
            color: {WHITE_TEXT};
            padding: 0.5rem 0.8rem;
            border-radius: 8px;
            margin-right: 1.5rem;
            font-weight: bold;
            display: inline-block;
            min-width: 35px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .heading-text {{
            color: {WHITE_TEXT};
            font-size: 1.7rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        /* Custom Messages */
        .stAlert {{
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            margin: 1.5rem 0;
        }}
        
        /* Success Message */
        .stAlert.st-success {{
            background-color: {PURPLE_LIGHT};
            border-color: {PURPLE_COLOR};
            color: {WHITE_TEXT};
        }}
        
        /* Info Message */
        .stAlert.st-info {{
            background-color: {NAVY_LIGHT};
            border-color: {NAVY_COLOR};
            color: {WHITE_TEXT};
        }}
        
        /* Upload Notification */
        .upload-notification {{
            background-color: white;
            border-left: 4px solid {PURPLE_COLOR};
            padding: 1rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        /* Progress Bar - Hide the streamlit default progress bar */
        .stProgress > div > div {{
            background-color: {PURPLE_COLOR};
            height: 8px;
            border-radius: 4px;
        }}
        
        .css-1p1nwyz, .stProgress {{
            display: none !important;
        }}
        
        /* File Info Card */
        .file-info-card {{
            background-color: white;
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }}
        
        .file-detail {{
            display: flex;
            padding: 0.7rem 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }}
        
        .file-detail-label {{
            font-weight: 600;
            color: {NAVY_COLOR};
            width: 35%;
        }}
        
        .file-detail-value {{
            color: {DARK_TEXT};
            width: 65%;
        }}
        
        /* Content Sections */
        .content-section {{
            background-color: {LIGHT_BG};
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        
        /* Metrics */
        .metric-container {{
            background-color: white;
            border-radius: 8px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            text-align: center;
            border-top: 4px solid {PURPLE_COLOR};
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {NAVY_COLOR};
            margin: 0.8rem 0;
        }}
        
        .metric-label {{
            font-size: 1.1rem;
            color: {DARK_TEXT};
            font-weight: 500;
        }}
        
        /* Download Button */
        .download-button {{
            background-color: {NAVY_COLOR};
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 6px;
            text-align: center;
            margin-top: 1.5rem;
            display: inline-block;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        .download-button:hover {{
            background-color: {PURPLE_COLOR};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        /* Header */
        .header-container {{
            display: flex;
            align-items: center;
            padding: 1.5rem;
            background-color: {LIGHT_BG};
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .app-title {{
            color: {NAVY_COLOR};
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            padding: 0;
        }}
        
        .app-subtitle {{
            color: {DARK_TEXT};
            font-size: 1.1rem;
            margin-top: 0.5rem;
            font-weight: 400;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 1.5rem;
            margin-top: 3rem;
            border-top: 1px solid rgba(0,0,0,0.1);
        }}
        
        /* JSON Display */
        .json-container {{
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid {NAVY_LIGHT};
            height: 100%;
        }}
        
        /* Responsive Adjustments */
        @media (max-width: 768px) {{
            .heading-container {{
                flex-direction: column;
                text-align: center;
            }}
            
            .heading-number {{
                margin-right: 0;
                margin-bottom: 0.8rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def styled_heading(number, text):
    """Generate a styled heading with a numbered label"""
    st.markdown(
        f"""
        <div class="heading-container">
            <div class="heading-number">{number}</div>
            <div class="heading-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def header():
    """Display the app header with embedded SVG icon to prevent broken images"""
    st.markdown(
        f"""
        <div class="header-container">
            <div style="margin-right: 1.5rem;">
                <!-- Embedded SVG soccer ball icon -->
                <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="{PURPLE_COLOR}">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-10.1l-2.12-2.12a.996.996 0 1 0-1.41 1.41L9.59 11.3c.39.39 1.02.39 1.41 0l4.24-4.24a.996.996 0 1 0-1.41-1.41L12 7.59l-1 1.31z"/>
                </svg>
            </div>
            <div>
                <h1 class="app-title">آساطير الغد - Soccer Skills Analyzer</h1>
                <p class="app-subtitle">Upload your soccer video to get an analysis of your skills</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def upload_video():
    """Handle video file upload and processing"""
    styled_heading("1", "Upload Your Video")
    
    st.markdown(
        """
        <div class="content-section">
            <p>Select a video file showing your soccer skills. We support MP4, MOV, and AVI formats.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        "Choose a soccer video file",
        type=["mp4", "mov", "avi"],
        help="Upload a video file of soccer skills to analyze",
    )
    
    if uploaded_file:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            # Get file details
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            
            # Read and write the file in one go
            data = uploaded_file.getvalue()
            tmp_file.write(data)
            
            # Get the temporary file path
            temp_file_path = tmp_file.name
        
        # Display file details with a custom styled notification instead of st.success
        st.markdown(
            f"""
            <div class="upload-notification">
                <div style="display: flex; align-items: center;">
                    <div style="margin-right: 12px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="{PURPLE_COLOR}">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    <div>
                        <span style="font-weight: 600; color: {NAVY_COLOR};">Video uploaded successfully</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Display video
            st.video(uploaded_file)
        
        with col2:
            # Show file details in a styled container with improved formatting
            st.markdown('<div class="file-info-card">', unsafe_allow_html=True)
            st.markdown(f'<h3 style="color: {NAVY_COLOR}; margin-bottom: 1rem; font-size: 1.3rem;">File Information</h3>', unsafe_allow_html=True)
            
            # Custom styled file details instead of st.json
            st.markdown(
                f"""
                <div class="file-detail">
                    <div class="file-detail-label">Filename:</div>
                    <div class="file-detail-value">{file_details["FileName"]}</div>
                </div>
                <div class="file-detail" style="border-bottom: none;">
                    <div class="file-detail-label">File Type:</div>
                    <div class="file-detail-value">{file_details["FileType"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Process button with more space
            st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
            if st.button("Analyze Soccer Skills", type="primary"):
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)  # Close content-section
                return temp_file_path, uploaded_file.name
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close content-section
            
    return None, None

def process_and_display_results(temp_file_path, original_filename):
    """Process the video and display results"""
    if not temp_file_path:
        return
    
    styled_heading("2", "Processing Video")
    
    # Create a placeholder for the processing status
    status_placeholder = st.empty()
    status_placeholder.info("Processing your video... This may take a few minutes.")
    
    try:
        # Process the video
        results = process_video(temp_file_path)
        
        # Clear the status message
        status_placeholder.empty()
        
        # Display results
        styled_heading("3", "Analysis Results")
        
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        
        # Create three columns for the scores with custom styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-container">
                    <p class="metric-label">Jumping with Ball</p>
                    <p class="metric-value">{results['jump_score']}/5</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(results['jump_score']/5)
            
        with col2:
            st.markdown(
                f"""
                <div class="metric-container">
                    <p class="metric-label">Running with Ball</p>
                    <p class="metric-value">{results['running_score']}/5</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(results['running_score']/5)
            
        with col3:
            st.markdown(
                f"""
                <div class="metric-container">
                    <p class="metric-label">Passing</p>
                    <p class="metric-value">{results['passing_score']}/5</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(results['passing_score']/5)
        
        # Overall score with improved styling
        st.markdown(
            f"""
            <div style='background-color:{NAVY_COLOR}; padding:30px; border-radius:12px; margin-top:30px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
                <h2 style='color:white; text-align:center; font-size:1.5rem; margin-bottom:1rem;'>Overall Performance Score</h2>
                <h1 style='color:{PURPLE_LIGHT}; text-align:center; font-size:5rem; font-weight:700; margin:0;'>{results['overall_score']:.1f}<span style='font-size:3rem; opacity:0.8;'>/5</span></h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display processing details with more space
        st.markdown("<div style='margin-top: 2.5rem;'>", unsafe_allow_html=True)
        st.info(f"Processing time: {results['processing_time']:.2f} seconds")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Option to download results as JSON with custom styling
        results_json = json.dumps(results, indent=4)
        
        st.markdown("<div style='text-align: center; margin-top: 2rem;'>", unsafe_allow_html=True)
        st.download_button(
            label="Download Results (JSON)",
            data=results_json,
            file_name=f"{Path(original_filename).stem}_results.json",
            mime="application/json",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close content-section
        
    except Exception as e:
        status_placeholder.error(f"Error processing video: {str(e)}")
        st.exception(e)
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

def main():
    """Main app function"""
    local_css()
    
    # Initialize session state for API endpoint
    if 'api_endpoint' not in st.session_state:
        st.session_state.api_endpoint = None
    
    # Add a section in the sidebar to set the API endpoint
    with st.sidebar:
        st.markdown(f"<h3 style='color: {NAVY_COLOR};'>Colab Connection</h3>", unsafe_allow_html=True)
        
        api_endpoint = st.text_input(
            "Enter Colab API URL", 
            value=st.session_state.api_endpoint if st.session_state.api_endpoint else "",
            placeholder="e.g., https://8abc-35-222-111-222.ngrok.io/analyze_video",
            help="Enter the public URL provided by ngrok when you run the colab.py notebook"
        )
        
        if api_endpoint:
            st.session_state.api_endpoint = api_endpoint
            st.success("API endpoint set! Using real model from Colab.")
        else:
            st.info("No API endpoint set. Using mock processor.")
            
        st.markdown("---")
    
    header()
    
    temp_file_path, original_filename = upload_video()
    
    if temp_file_path:
        process_and_display_results(temp_file_path, original_filename)
    
    # Footer with improved styling
    st.markdown(
        f"""
        <div class="footer">
            <p style='color: {NAVY_COLOR}; font-weight: 500;'>
                 <span style='color: {PURPLE_COLOR};'>❤️</span>  آساطير الغد (Legends of Tomorrow) Project
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 