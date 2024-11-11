from flask import Flask, request, jsonify
from flask_cors import CORS
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pika
import redis
import json
import uuid
import hashlib

app = Flask(__name__)
CORS(app)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize PersistentClient and load the collection
client = PersistentClient(
    path="/tmp/chroma_data",  # Adjust this path as needed
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection("pdf_knowledge_base")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to create a Redis cache key based on the query
def get_cache_key(query):
    return hashlib.sha256(query.encode()).hexdigest()

@app.route("/submit_query", methods=["POST"])
def submit_query():
    user_query = request.json.get("query")
    correlation_id = str(uuid.uuid4())

    # Check if the query result is already cached in Redis
    cache_key = get_cache_key(user_query)
    cached_response = redis_client.get(cache_key)

    if cached_response:
        # Return the cached response if it exists
        print("Found cached response...\n")
        return jsonify(json.loads(cached_response))

    # Set up a new RabbitMQ connection and channel for each request
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the queues to ensure they exist
    channel.queue_declare(queue='query_queue')
    channel.queue_declare(queue='response_queue')

    # Publish the query to RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key='query_queue',
        properties=pika.BasicProperties(
            reply_to='response_queue',
            correlation_id=correlation_id
        ),
        body=json.dumps({"query": user_query})
    )

    # Wait for response from the response queue
    try:
        for method_frame, properties, body in channel.consume('response_queue', inactivity_timeout=5):
            if method_frame is None:
                break  # Timeout reached with no message
            if properties and properties.correlation_id == correlation_id:
                channel.basic_ack(method_frame.delivery_tag)
                response_data = json.loads(body)

                # Cache the response in Redis with a TTL (e.g., 1 hour)
                redis_client.setex(cache_key, 3600, json.dumps(response_data))
                
                if connection.is_open:
                    connection.close()  # Close the connection after receiving the response
                return jsonify(response_data)  # Send response back to frontend
    except Exception as e:
        print(f"Error while consuming from RabbitMQ: {e}")
    finally:
        if connection.is_open:
            connection.close()

    # If no response was received, return a timeout response
    return jsonify({"response": "No relevant documents found or timeout occurred."}), 504


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
