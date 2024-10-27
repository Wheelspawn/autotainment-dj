import streamlit as st
import cv2
import os
import time
import base64
import random

from groq import Groq
from playsound import playsound

# Set up the output folder for saved frames
output_folder = "VideoFrames"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Function to capture and save frames from the video stream
def stream_video_to_images(video_source=0):
    cap = cv2.VideoCapture(video_source)
    frame_count = 0
    
    stframe = st.empty()  # Placeholder for displaying frames in Streamlit

    client = Groq(    
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Display the frame in Streamlit
        stframe.image(frame, channels="BGR", caption=f"Frame")
        
        # Save the frame as an image in the output folder
        frame_path = os.path.join(output_folder, f"frame.jpg")

        encode = encode_image(frame_path)

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
                                    "url": f"data:image/jpeg;base64,{encode}",
                                }
                            }
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": ""
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
        
        print(completion)
        
        if 'dancing' in completion:
            playsound('strobe.mp3')
        elif 'sitting' in completion:
            playsound('sunflower.mp3')
        else:
            pass

        cv2.imwrite(frame_path, frame)
        
        frame_count += 1
        time.sleep(1.5)  # Adjust the delay to control frame rate

    cap.release()

# Streamlit App Interface
st.title("Video Stream to Images")
source_option = st.selectbox("Select Video Source", ["Webcam", "Video File"])

if source_option == "Webcam":
    stream_video_to_images(video_source=1)
elif source_option == "Video File":
    video_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
    if video_file is not None:
        video_path = os.path.join("temp_video", video_file.name)
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        stream_video_to_images(video_source=video_path)

st.write(f"Frames saved in folder: `{output_folder}`")
