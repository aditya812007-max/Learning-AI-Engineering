import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API ERROR")

client = Groq(api_key=my_api_key)
model = "llama-3.3-70b-versatile"

def llm_ans(prompt):
    message = {
        "role":"user",
        "content":prompt
    }
    messages = [message]
    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer

prompt = """
#ROLE:
you are a customer support chatbot for a electronics company
#TASK:
solve and classify user's complaints
#CONSTRAINTS:
classify all the issues in these three categories Tech, Refund, Return
#RESPONSE FORMAT:
answer only in one word
#EXAMPLE:
if the customer says he has issue with the laptop turning on classify it as Tech
#FALLBACK:
if the issue being raised is completly unrelated then classify it as OTHERS
this is user's complaint:
i dont like this laptop i bought and i want my money back, if it doesnt turn on
"""

print(llm_ans(prompt))