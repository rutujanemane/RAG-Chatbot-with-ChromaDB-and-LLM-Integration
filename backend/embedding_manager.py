from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pdfplumber
import os

# Initialize PersistentClient and load the collection
client = PersistentClient(
    path="/tmp/chroma_data",  # Persistent storage path
    settings=Settings(anonymized_telemetry=False),
)


def extract_text_from_pdf(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        year = (
            "2023" if "2023" in file_path else "2024"
        )  # Tagging each chunk with the year for reference
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                chunks = text.split("\n\n")  # Split text into chunks
                for chunk_num, chunk in enumerate(chunks):
                    data.append(
                        {
                            "id": f"{os.path.basename(file_path)}_page{page_num}_chunk{chunk_num}",
                            "text": chunk.strip(),
                            "source": file_path,
                            "page": page_num,
                            "year": year,  # Add year metadata for backend use
                        }
                    )
    return data


def setup_collection():
    # Create or get collection
    collection_name = "pdf_knowledge_base"
    if collection_name in [col.name for col in client.list_collections()]:
        collection = client.get_collection(collection_name)
    else:
        collection = client.create_collection(collection_name)

    # Load SentenceTransformer model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Extract and add data from PDFs
    pdf_files = ["../data/SOFI-2023.pdf", "../data/SOFI-2024.pdf"]
    for pdf_file in pdf_files:
        pdf_data = extract_text_from_pdf(pdf_file)
        for item in pdf_data:
            embedding = model.encode(item["text"]).tolist()
            collection.add(
                ids=[item["id"]],
                documents=[item["text"]],
                embeddings=[embedding],
                metadatas=[
                    {
                        "source": item["source"],
                        "page": item["page"],
                        "year": item["year"],
                    }
                ],
            )

    print("Collection setup complete.")


# Run the setup function
setup_collection()


def delete_collection_if_exists(collection_name):
    try:
        # List current collections to verify existence
        available_collections = [col.name for col in client.list_collections()]

        if collection_name in available_collections:
            # Delete the collection if it exists
            client.delete_collection(collection_name)
            print(f"Collection '{collection_name}' has been successfully deleted.")
        else:
            print(f"Collection '{collection_name}' does not exist.")

    except Exception as e:
        print(f"Error while deleting the collection '{collection_name}': {e}")


# Specify the collection name to delete
# collection_name = "pdf_knowledge_base"

# Run the function
# delete_collection_if_exists(collection_name)
