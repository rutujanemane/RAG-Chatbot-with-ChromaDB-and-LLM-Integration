from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configure PersistentClient for ChromaDB with the persistent storage path
client = PersistentClient(
    path="/tmp/chroma_data",  # Directly specify the persistent storage path
    settings=Settings(
        anonymized_telemetry=False
    ),  # Optional: add other settings if needed
)

# Access the collection and run a sample query
collection = client.get_collection("pdf_knowledge_base")
model = SentenceTransformer("all-MiniLM-L6-v2")
sample_query = "What is food security?"
query_embedding = model.encode(sample_query).tolist()

results = collection.query(query_embedding)
print("Query Results:", results)
