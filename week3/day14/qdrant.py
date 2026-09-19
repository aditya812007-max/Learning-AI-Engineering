import os
from groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
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

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
print("Connected to Qdrant Cloud!")
groq_client = Groq(api_key=groq_api_key)

COLLECTION_NAME = "knowledge"
EMBEDDING_SIZE = 384

if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting Existing collection {COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)

client.create_collection(collection_name=COLLECTION_NAME,vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE))

print(f"Created Collection: {COLLECTION_NAME}")
print(f"Embedding size: {EMBEDDING_SIZE}")
print("Distance: COSINE")

with open("knowledge.txt", "r", encoding="utf-8") as f:
    document = [line.strip() for line in f if line.strip()]
print(f"Loaded {len(document)} documents")

print("Loading Embedding Model....")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model ready!")

embeddings = model.encode(document)
print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size: {len(embeddings[0])}")

points = []

for i, embedding in enumerate(embeddings):
    point = PointStruct(
        id=i + 1,
        vector=embedding.tolist(),
        payload={
            "text": document[i]
        }
    )

    points.append(point)


client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"Uploaded {len(points)} documents to Qdrant!")


def search(query, top_k=3):
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    ).points

    return results


question = "How much gym reimbursement do I get?"

results = search(question, top_k=3)

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


context = "\n".join(
    result.payload["text"]
    for result in results
)

answer = ask_llm(question, context)

print("\nFinal Answer:")
print(answer)