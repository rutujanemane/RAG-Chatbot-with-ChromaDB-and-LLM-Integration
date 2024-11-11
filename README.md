# **RAG Chatbot with ChromaDB and LLM Integration**

This project is a **Retrieval-Augmented Generation (RAG) Chatbot** that combines ChromaDB for document retrieval and a large language model (LLM) for answer generation. The chatbot provides intelligent responses based on information from provided PDFs, making it useful for complex document-driven Q&A.

## **Features**

- **Context-Aware Responses**: Retrieves the closest text match from multiple documents.
- **Document Search**: Searches across multiple PDFs to retrieve relevant content.
- **Efficient Processing**: Uses Redis for caching and RabbitMQ for task management.

## **Tech Stack**

- **Backend**: Python, Flask, ChromaDB, Sentence Transformers, OpenAI API
- **Frontend**: HTML, JavaScript
- **Message Queue & Cache**: RabbitMQ, Redis

## **Setup**

**Clone the repository** and **install dependencies**:
   ```bash
   git clone https://github.com/patilkalpesh/RAG-Chatbot-with-ChromaDB-and-LLM-Integration.git

   cd RAG-Chatbot-with-ChromaDB-and-LLM-Integration

   pip install -r requirements.txt
```
**Add your OpenAI API key**:
   ```
   export OPENAI_API_KEY='your_api_key'
```

**RabbitMQ**:
   ```bash
   docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```
**Redis**:
```bash
redis-server
```
**Run Backend**:
   ```bash
   cd backend

   python embedding_manager.py

   python worker.py

   python main.py
```
