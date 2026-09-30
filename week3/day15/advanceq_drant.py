import os
import json
from groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType
from sentence_transformers import SentenceTransformer

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ API KEY NOT FOUND")
if not qdrant_url:
    raise ValueError("Qdrant URL NOT FOUND")
if not qdrant_api_key:
    raise ValueError("Qdrant API KEY NOT FOUND")

qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, prefer_grpc=False, check_compatibility=False)
print("Connected to Qdrant Cloud!")
groq_client = Groq(api_key=groq_api_key)

COLLECTION_NAME = "knowledge_json"
EMBEDDING_SIZE = 384

if qdrant_client.collection_exists(collection_name=COLLECTION_NAME):
    print(f"Deleting Existing collection {COLLECTION_NAME}")
    qdrant_client.delete_collection(collection_name=COLLECTION_NAME)

qdrant_client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
)

print(f"Created Collection: {COLLECTION_NAME}")
print(f"Embedding size: {EMBEDDING_SIZE}")
print("Distance: COSINE")

qdrant_client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD,
)
with open("knowledge.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

print("Loading embedding model...")
model= SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model ready!")
texts = [document["text"] for document in documents]
embedding = model.encode(texts)
print(f"Generated {len(embedding)} embeddings")
print(f"Embedding size: {len(embedding[0])}")

points= []
for i in range(len(documents)):
    point = PointStruct(
        id = i+1,
        vector = embedding[i].tolist(),
        payload = documents[i]
    )
    points.append(point)

qdrant_client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)    
print(f"Uploaded {len(documents)} documents to Qdrant")

def search(query, top_k=3):
    query_vector = model.encode(query).tolist()

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results

def search_with_filter(query, query_filter=None, top_k=3):


    query_vector = model.encode(query).tolist()


    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter,
    ).points


    return results

reimbursement_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        )
    ]
)

query = "How many vacation days do I get?"

results = search_with_filter(query, reimbursement_filter,top_k=3)

print("\nSearch results:")

for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print()

def ask_llm(question, context):
    prompt = f"""
Answer the question using only the information provided below.
Context:{context}
Question:{question}
If the answer is not present in the context, say:
"I don't know based on the provided information."
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

question = "How many vacation days do I get?"

results = search(question, top_k=3)

context = "\n".join(
    result.payload["text"]
    for result in results
)


answer = ask_llm(question, context)


print("\nFinal Answer:")
print(answer)

