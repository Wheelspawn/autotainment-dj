import csv
import time
import os
from groq import Groq

def main():
    
    client = Groq(    
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    
    while True:
    
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "If the people in this photo are standing or dancing, output 'dancing'. If they are sitting, output 'sitting'. If there are no people in the photo, output 'empty'. You are outputting a single keyword. Do not output anything other than one of these three words. Do not output a sentence or paragraph. Do not output any punctuation."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/3/38/Two_dancers.jpg"
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
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
