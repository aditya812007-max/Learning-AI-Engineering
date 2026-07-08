import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API ERROR")

client = Groq(api_key = my_api_key)

model = "llama-3.3-70b-versatile"

role = "user"

prompt = "who are you?"

message = {
           "role":role,
           "content":prompt
}

messages = [message]

response = client.chat.completions.create(model = model, messages = messages)

answer = response.choices[0].message.content
print(##############################
    )
print(answer)