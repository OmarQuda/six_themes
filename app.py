import streamlit as st
import tempfile
import os
import time
import json
import random
from pathlib import Path
import requests

# Connection to the remote prediction endpoint
def predict_remote(value, api_url):
    """
    Send prediction request to remote API endpoint
    
    Args:
        value (float): Value to be predicted
        api_url (str): URL to the FastAPI endpoint
        
    Returns:
        dict: Prediction result
    """
    # Prepare the request payload
    payload = {"value": float(value)}
    
    try:
        # Make the request to the API
        response = requests.post(f"{api_url}/predict", json=payload)
        
        # Check for successful response
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Original mock implementation (used as fallback)
def predict_local(value):
    """
    Mock implementation of prediction when API is not available
    
    Args:
        value (float): Value to be predicted
        
    Returns:
        dict: Mock prediction results
    """
    # Simulate processing time
    time.sleep(1)
    
    # Simple doubling function (matching the colab.py model)
    prediction = value * 2
    
    # Compile results
    results = {
        "prediction": prediction,
        "processing_time": random.uniform(0.5, 1.5)
    }
    
    return results

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

def main():
    """Main app function"""
    local_css()
    header()
    
    # Add input field for API URL
    st.sidebar.title("API Configuration")
    api_url = st.sidebar.text_input(
        "FastAPI Endpoint URL",
        value="http://localhost:8000",
        help="Enter the LocalTunnel URL from Colab (e.g., https://xxxx.loca.lt)"
    )
    use_remote_api = st.sidebar.checkbox("Use Remote API", value=True, help="If unchecked, will use local mock processing")
    
    # If API URL is not provided and remote API is checked, show warning
    if not api_url and use_remote_api:
        st.sidebar.warning("Please enter the LocalTunnel URL from your Colab notebook")
    
    # New interface for prediction instead of video upload
    styled_heading("1", "Simple Prediction Model")
    
    st.markdown(
        """
        <div class="content-section">
            <p>Enter a value to be processed by the prediction model. The model will multiply your input by 2.</p>
            <p><small>The model is running in Google Colab and exposed via LocalTunnel. If the connection fails, it will fallback to local processing.</small></p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Input form
    input_value = st.number_input("Enter a value", value=5.0, step=0.5)
    
    if st.button("Get Prediction", type="primary"):
        # Show processing status
        status_placeholder = st.empty()
        status_placeholder.info("Processing your request...")
        
        try:
            # Process the request using either remote or local processing
            if use_remote_api and api_url:
                status_placeholder.info(f"Sending request to API at {api_url}...")
                results = predict_remote(input_value, api_url)
                if results is None:
                    # Fallback to local processing if remote fails
                    status_placeholder.warning("Remote API failed. Falling back to local processing. Make sure your Colab notebook is running and the LocalTunnel URL is correct.")
                    results = predict_local(input_value)
            else:
                status_placeholder.info("Using local processing...")
                results = predict_local(input_value)
            
            # Clear the status message
            status_placeholder.empty()
            
            # Display results
            styled_heading("2", "Prediction Results")
            
            st.markdown('<div class="content-section">', unsafe_allow_html=True)
            
            # Display the prediction result
            st.markdown(
                f"""
                <div style='background-color:{NAVY_COLOR}; padding:30px; border-radius:12px; margin-top:10px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
                    <h2 style='color:white; text-align:center; font-size:1.5rem; margin-bottom:1rem;'>Model Prediction</h2>
                    <h1 style='color:{PURPLE_LIGHT}; text-align:center; font-size:5rem; font-weight:700; margin:0;'>{results['prediction']}</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # If we have processing time in the results
            if 'processing_time' in results:
                st.markdown("<div style='margin-top: 2.5rem;'>", unsafe_allow_html=True)
                st.info(f"Processing time: {results['processing_time']:.2f} seconds")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Option to download results as JSON
            results_json = json.dumps(results, indent=4)
            
            st.markdown("<div style='text-align: center; margin-top: 2rem;'>", unsafe_allow_html=True)
            st.download_button(
                label="Download Results (JSON)",
                data=results_json,
                file_name="prediction_results.json",
                mime="application/json",
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close content-section
            
        except Exception as e:
            status_placeholder.error(f"Error processing request: {str(e)}")
            st.exception(e)
    
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