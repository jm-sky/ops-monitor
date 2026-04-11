# Open-Source Examples

Several public projects demonstrate JSON-based AI/FastAPI integrations:

- Azure OpenAI FastAPI Chat: Microsoft's openai-chat-backend-fastapi is a sample FastAPI backend that streams Azure OpenAI (GPT) responses. It uses Docker and Azure Container Apps, and shows how to accept JSON chat requests and stream back JSONL responses for a chat UI.

- Assistant API Streaming: The xbreid/fastapi-assistant-streaming repo (from a Medium tutorial) integrates FastAPI with OpenAI's new Assistant API using SSE streaming. It handles JSON chat payloads, conversation threads, and streaming. This is a good model for asynchronous JSON exchanges.

- Simple FastAPI/OpenAI Example: The simple-openai-fastapi-server repo by thomassuedbroecker provides endpoints that accept JSON (text input, file upload, or context+question) and return the model's JSON response. It illustrates using security (Basic Auth) and integrating file uploads with LLMs.

- Neo4j GraphRAG: Neo4j's Knowledge Graph Builder (LLMGraphBuilder) is a FastAPI-based back end that combines LangChain with a Neo4j graph to extract information from documents and serve it via a GraphRAG interface. Although focused on document-to-graph, it exemplifies an AI+FastAPI service with JSON APIs (loading documents, querying graphs).


These examples all use JSON payloads and demonstrate structuring endpoints around LLM calls, with best practices like stream handling, dependency injection, and typed Pydantic models.

