from http import client
import os 
from pathlib import Path
from pyexpat import model
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API ERROR")
client = Groq(api_key=my_api_key)
model= ("llama-3.3-70b-versatile")

prompt = """
how does the internet work ?
"""

message = {
    "role":"user",
    "content":prompt
}

messages = [message]

#response  = client.chat.completions.create(model=model, messages=messages)
#answer = response.choices[0].message.content
#print(answer)

stream  = client.chat.completions.create(model=model, messages=messages, stream=True)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

        