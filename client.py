import streamlit as st
import cv2
import os
import time
import base64
from groq import Groq
from playsound import playsound
from PIL import Image
import numpy as np
import io

# Initialize session state variables
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Set up the output folder for saved frames
output_folder = "VideoFrames"
os.makedirs(output_folder, exist_ok=True)

def get_available_cameras():
    """Check available camera indices"""
    available_cameras = []
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

def encode_image(frame):
    """Encode frame directly from numpy array to base64"""
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        raise ValueError("Could not encode image")
    return base64.b64encode(buffer).decode('utf-8')

def play_sound(sound_type):
    """Play sound in a way that won't block the main thread"""
    try:
        playsound(f'{sound_type}.mp3', block=False)
    except Exception as e:
        st.error(f"Error playing sound: {e}")

def process_frame(frame, client):
    """Process a single frame through Groq API"""
    try:
        # Encode frame directly
        encoded_frame = encode_image(frame)
        
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "If the people in this photo are standing or dancing, output 'dancing'. If they are sitting, output 'sitting'. If there are no people in the photo, or there is no photo, output 'empty'. You are outputting a single keyword. Do not output anything other than one of these three words. Do not output a sentence or paragraph. Do not output any punctuation."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_frame}",
                            }
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        result = completion.choices[0].message.content.lower().strip()
        
        # Map result to sound file
        sound_mapping = {
            'dancing': 'strobe',
            'sitting': 'sunflower',
            'empty': 'silence'
        }
        
        if result in sound_mapping:
            play_sound(sound_mapping[result])
        
        return result
    except Exception as e:
        st.error(f"Error processing frame: {e}")
        return None

def stream_video_to_images(video_source=0):
    """Main video processing function"""
    try:
        # Try to open the video source
        cap = cv2.VideoCapture(video_source)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            st.error(f"Error: Could not open video source {video_source}")
            return

        # Initialize Groq client
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            st.error("Error: GROQ_API_KEY not found in environment variables")
            return
        
        client = Groq(api_key=api_key)
        
        # Create placeholders
        frame_display = st.empty()
        status_text = st.empty()
        
        st.session_state.processing = True
        
        while cap.isOpened() and st.session_state.processing:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read frame from video source")
                break
                
            # Convert BGR to RGB for Streamlit display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_display.image(frame_rgb, caption="Video Feed")
            
            # Save frame and process
            frame_path = os.path.join(output_folder, "current_frame.jpg")
            cv2.imwrite(frame_path, frame)
            
            result = process_frame(frame, client)
            if result:
                status_text.text(f"Detected: {result}")
            
            time.sleep(1.5)  # Delay between frames
            
        cap.release()
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if 'cap' in locals():
            cap.release()

def main():
    st.title("Video Stream to Images")
    
    # Add a stop button
    if st.session_state.processing:
        if st.button("Stop Processing"):
            st.session_state.processing = False
    
    source_option = st.selectbox("Select Video Source", ["Webcam", "Video File"])
    
    if source_option == "Webcam":
        # Get available cameras
        available_cameras = get_available_cameras()
        
        if not available_cameras:
            st.error("No cameras detected. Please check your camera connection.")
            return
            
        # Let user select from available cameras
        camera_index = st.selectbox(
            "Select Camera",
            available_cameras,
            format_func=lambda x: f"Camera {x} {'(Built-in)' if x == 0 else ''}"
        )
        
        if st.button("Start Webcam"):
            stream_video_to_images(video_source=camera_index)
    
    elif source_option == "Video File":
        video_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
        if video_file is not None:
            # Create temp directory if it doesn't exist
            os.makedirs("temp_video", exist_ok=True)
            
            # Save uploaded file
            video_path = os.path.join("temp_video", video_file.name)
            with open(video_path, "wb") as f:
                f.write(video_file.read())
            
            if st.button("Process Video"):
                stream_video_to_images(video_source=video_path)
    
    st.write(f"Frames are being saved in: `{output_folder}`")

if __name__ == "__main__":
    main()