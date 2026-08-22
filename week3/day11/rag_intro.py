import os
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("api key not found")

model = "allam-2-7b"
client = Groq(api_key=my_api_key)
"""
i used this to check what are the availble models

models = client.models.list()
for m in models.data:
    print(m.id)
"""
knowledge_base={
    "age":"Aditya is 19 years old",
    "education":"Aditya is currently pursing 3rd year of Btech CSE with specilisation in Artifical Intelligence and Machine Learning",
    "college":"SRM IST Trichy"
}

def retireve_info(question):
    question=question.lower()
    if "age" in question or "old" in question:
        return knowledge_base["age"]
    elif "education" in question:
        return knowledge_base["education"]
    elif "college" in question:
        return knowledge_base["college"]
    else:
        return None

def ask_llm(question):
    context = retireve_info(question)
    sys_prompt = f"""answer in 1 line only. Answer only based on this context:{context}. do not hallucinate"""
    sys_message = {
            "role":"system",
            "content":sys_prompt
        }
    message = {
        "role":"user",
        "content":question
    }
    
    messages=[sys_message, message]
    response = client.chat.completions.create(model=model, messages=messages)
    answer = response.choices[0].message.content
    return answer

question = "what is Aditya's education?"
print(ask_llm(question))