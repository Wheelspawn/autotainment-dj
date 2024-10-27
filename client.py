import streamlit as st
import cv2
import os
import time
from groq import Groq

# Set up the output folder for saved frames
output_folder = "VideoFrames"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Groq client
client = Groq(    
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Function to capture and save frames from the video stream
def stream_video_to_images(video_source=0):
    cap = cv2.VideoCapture(video_source)
    frame_count = 0
    
    stframe = st.empty()  # Placeholder for displaying frames in Streamlit
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Display the frame in Streamlit
        stframe.image(frame, channels="BGR", caption=f"Frame")
        
        # Save the frame as an image in the output folder
        frame_path = os.path.join(output_folder, f"frame.jpg")
        cv2.imwrite(frame_path, frame)
        
        frame_count += 1
    
        cap.release()

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
                                "url": f"data:image/jpeg;base64,{frame_path}",
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

        print(completion.choices[0].message)
            
        time.sleep(0.5)  # Adjust the delay to control frame rate

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
