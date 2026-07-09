import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha h bhai ?")

client = Groq(api_key = my_api_key)

model = "llama-3.3-70b-versatile"

role = "user"

prompt1 = "hi"
prompt2 = "who is seedhe maut?"
prompt3 = "write an essay of 1000 wrods on seedheamut"

prompts = [prompt1, prompt2, prompt3]

for prompt in prompts:
    message = {
        "role":role,
        "content":prompt
    }
    messages = [message]
    response = client.chat.completions.create(model=model, messages=messages, max_tokens=500)
    usage = response.usage
    print(f"Promprt: {prompt}, prompt token --->{usage.prompt_tokens}, response token ---> {usage.completion_tokens}, total token ---> {usage.total_tokens}")