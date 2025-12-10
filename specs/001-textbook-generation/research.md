# Research: AI-Native Textbook with AI Chatbot

## Decision: Technology Stack Selection
**Rationale**: Selected a technology stack that aligns with the project's constitution principles of simplicity, free-tier compatibility, and lightweight design. Docusaurus for the frontend provides a proven, efficient static site generation system. FastAPI for the backend offers high performance with minimal code. Qdrant as the vector database provides efficient similarity search for RAG functionality.

**Alternatives considered**:
- Frontend: Next.js vs Docusaurus vs VuePress - Docusaurus chosen for its textbook-focused features and simplicity
- Backend: Express.js vs FastAPI vs Flask - FastAPI chosen for async performance and built-in OpenAPI docs
- Vector DB: Pinecone vs Weaviate vs Qdrant - Qdrant chosen for open-source nature and free-tier availability

## Decision: AI Model Selection
**Rationale**: For the AI chatbot functionality, using OpenAI API or an open-source alternative (like Ollama with local models) to provide responses based only on textbook content. This ensures RAG integrity while maintaining free-tier compatibility through careful token management.

**Alternatives considered**:
- OpenAI API vs Anthropic Claude vs Local models (Ollama/Llama.cpp) - OpenAI API chosen for reliability, Claude for safety, Local models for cost control
- Final choice will depend on free-tier requirements and performance needs

## Decision: Deployment Architecture
**Rationale**: Separating the textbook frontend (Docusaurus) from the AI backend (FastAPI) allows for independent scaling and development. Docusaurus can be deployed statically while the AI backend handles dynamic queries.

**Alternatives considered**:
- Monolithic vs Microservices vs Serverless - Chosen a hybrid approach with static frontend and dynamic backend API
- Cloud providers: Vercel/Netlify for frontend, Railway/Hetzner for backend, or all-in-one solution

## Decision: Embedding Strategy
**Rationale**: Using lightweight embedding models to stay within free-tier limits while maintaining quality. Chunking textbook content into appropriate sizes for vector storage and retrieval.

**Alternatives considered**:
- Model choices: OpenAI embeddings vs Sentence Transformers vs Local models
- Chunk sizes: 256 vs 512 vs 1024 tokens - 512 chosen as balance between context and efficiency