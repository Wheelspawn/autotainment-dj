import csv
import time
import cv2
import os
from groq import Groq

import streamlit as st
st.title('Autonomous DJ')

import base64
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def main():
    
    # Path to your image

    image_path = "/home/nsage/Pictures/empty.jpeg"
    # Getting the base64 string
    base64_image = encode_image(image_path)
    
    client = Groq(    
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    while True:
        
        try:
            
            cap = cv2.VideoCapture(0)
            
            stframe = st.empty()  # Placeholder for displaying frames in Streamlit
            
            ret, frame = cap.read()
            
            # Display the frame in Streamlit
            stframe.image(frame, channels="BGR", caption=f"Frame")
            
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
                                    "url": f"data:image/jpeg;base64,{frame}",
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
        
            time.sleep(1)
            
        except:
            pass

if __name__ == "__main__":
    main()
