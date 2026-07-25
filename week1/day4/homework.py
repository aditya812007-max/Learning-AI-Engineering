import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API ERROR")

client = Groq(api_key=my_api_key)

model = "llama-3.3-70b-versatile"


# ---------- Step 1: read the resume (pdf or word) ----------
def read_resume(file_path):
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text = text + (page.extract_text() or "")
        return text

    elif path.suffix.lower() == ".docx":
        doc = Document(path)
        text = ""
        for para in doc.paragraphs:
            text = text + para.text + "\n"
        return text

    raise ValueError("Only .pdf or .docx files are supported")


# ---------- Step 2: HR gives a list of things to look for ----------
hr_requirements = {
    "skills": ["Python", "SQL", "Machine Learning", "Git"],
    "experience": "2+ years as a software / data engineer",
    "projects": ["a data pipeline project", "an ML model project"],
}


# ---------- Step 3 + 4: extract from resume AND match against HR list ----------
class Match(BaseModel):
    name: str
    email: str
    matched_skills: list[str]
    missing_skills: list[str]
    experience_match: bool
    projects_match: bool
    match_percentage: float
    verdict: str


schema = Match.model_json_schema()

response_format = {
    "type": "json_object"
}

resume_path = r"D:\Downloads\ADITYA BISWAL RESUME.pdf"  # change this to your resume file (.pdf or .docx)
resume_text = read_resume(resume_path)

system_prompt = f"""
You are an HR screening assistant.
You are given a candidate's resume and a list of requirements from HR.

HR requirements:
{json.dumps(hr_requirements, indent=2)}

Compare the resume against the HR requirements. Then return JSON strictly
following this schema:
{schema}

Rules:
- matched_skills: HR skills the candidate clearly has.
- missing_skills: HR skills the candidate does NOT have.
- experience_match: true if the candidate meets the experience requirement.
- projects_match: true if the candidate has projects similar to the HR list.
- match_percentage: a number from 0 to 100 for how well the resume matches HR needs.
- verdict: one short sentence saying whether to shortlist the candidate.
"""

message_system = {
    "role": "system",
    "content": system_prompt
}

prompt = f"""
Here is the resume:
{resume_text}
"""

message = {
    "role": "user",
    "content": prompt
}

messages = [message_system, message]

response = client.chat.completions.create(
    model=model, messages=messages, response_format=response_format
)

answer = response.choices[0].message.content
print(answer)

# ---------- validate with pydantic ----------
data_file = json.loads(answer)
result = Match(**data_file)

print("\n--- RESULT ---")
print("Name:", result.name)
print("Email:", result.email)
print("Matched skills:", result.matched_skills)
print("Missing skills:", result.missing_skills)
print("Experience match:", result.experience_match)
print("Projects match:", result.projects_match)
print("Match percentage:", result.match_percentage, "%")
print("Verdict:", result.verdict)