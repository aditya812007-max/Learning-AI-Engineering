import os
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a)*(np.linalg.norm(b)))

model = SentenceTransformer("all-MiniLM-L6-v2")
text = "I WANT TO BE AN AI ENGINEER"

embedding=model.encode(text)
print(embedding.shape)
print(embedding[:10])

t1 = "I like to play games on my pc"
t2 = "I love animals"

v1=model.encode(t1)
v2=model.encode(t2)
print(cosine_similarity(v1,v2))

