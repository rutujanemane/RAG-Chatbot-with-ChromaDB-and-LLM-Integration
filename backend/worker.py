import pika
import json
import openai
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialize OpenAI API key
openai.api_key = 'Your-API-Key'

# Initialize ChromaDB and SentenceTransformer
client = PersistentClient(
    path="/tmp/chroma_data",
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection("pdf_knowledge_base")
model = SentenceTransformer("all-MiniLM-L6-v2")

# RabbitMQ connection setup
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

channel.queue_declare(queue="query_queue")
channel.queue_declare(queue="response_queue")


# Function to generate a refined response using OpenAI
def generate_openai_response(user_query, context_text):
    prompt = f"User query: {user_query}\n\nContext:\n{context_text}\n\nPlease provide a concise and relevant answer based on this information."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if available
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise answers based on provided context.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "An error occurred while generating the response with OpenAI."


# Process function to handle incoming queries
def process_query(ch, method, properties, body):
    # Decode query and process it
    request_data = json.loads(body)
    user_query = request_data.get("query")
    query_embedding = model.encode(user_query).tolist()

    # Query the ChromaDB collection and retrieve top 5 matches
    results = collection.query(
        query_embedding, include=["documents", "metadatas", "distances"], n_results=5
    )

    response_data = {"response": "No relevant documents found"}  # Default response

    # Check if there are results
    if "documents" in results and results["documents"]:
        # Sort and gather the top 5 most relevant results
        top_matches = sorted(
            [
                {
                    "text": doc,
                    "source": meta.get("source"),
                    "page": meta.get("page"),
                    "year": meta.get("year"),
                    "similarity": dist,
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ],
            key=lambda x: x["similarity"],
        )[:5]  # Get only the top 5

        # Combine top 5 responses into a single context
        context_text = "\n\n".join([match["text"] for match in top_matches])

        # Generate a refined response from OpenAI
        openai_response = generate_openai_response(user_query, context_text)

        # Prepare response data
        response_data = {
            "response": openai_response,
            "context": top_matches,  # Include original contexts for reference
        }

    # Publish the refined response back to response_queue
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response_data),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Start consuming messages from query_queue
channel.basic_consume(queue="query_queue", on_message_callback=process_query)
print("Worker is waiting for messages in query_queue. To exit, press CTRL+C")
channel.start_consuming()
