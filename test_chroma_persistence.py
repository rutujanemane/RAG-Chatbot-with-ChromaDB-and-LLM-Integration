from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client with persistent storage
client = Client(Settings(persist_directory="chroma_data"))

# Create a collection and add a sample document
try:
    collection = client.create_collection("test_persistence_collection")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Add a sample document
    doc_text = "This is a test document for persistence."
    embedding = model.encode(doc_text).tolist()
    collection.add(
        ids=["test_id"],
        documents=[doc_text],
        embeddings=[embedding],
        metadatas=[{"source": "test_source"}],
    )
    print("Sample document added to collection.")
except Exception as e:
    print("Error during collection creation or document addition:", e)

# List collections to verify persistence
collections = client.list_collections()
print("Available Collections after setup:", collections)
