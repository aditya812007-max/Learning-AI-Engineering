import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv 
from pydantic import BaseModel

load_dotenv() 

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API ERROR")

client = Groq(api_key = my_api_key)

model = "llama-3.3-70b-versatile"

role = "user"

class Ticket(BaseModel): 
    name:str
    email:str
    issue:str
schema = Ticket.model_json_schema() 

response_format = {
    "type":"json_object"
}

system_prompt = f"""
Extract the personal information from the ticket strictly based on this schema and give a json output.
{schema}
""" 
message_system={
    "role": "system",
    "content": system_prompt
}

text = "hello my name is aditya biswal, i live in tamilnadu and love listening to hiphop, gym, playing video games and coding, i had purchased a keyboard which is a shitty ass keyboard and its USB A isnt working anymore; my gmail is aditya812007@gmail.com, my phone number is 9680757969"
prompt = f"""
{text}
""" 

message = {
           "role":role,
           "content":prompt
} 

messages = [message_system, message] 

response = client.chat.completions.create(model = model, messages = messages, response_format = response_format)

answer = response.choices[0].message.content

print(answer)

import json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)

print(ticket.name)
print(ticket.email)
print(ticket.issue)
