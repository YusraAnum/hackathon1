# Quickstart Guide: AI-Native Textbook with AI Chatbot

## Prerequisites
- Node.js 18+
- Python 3.11+
- Git

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Set up the frontend (Docusaurus textbook)
```bash
cd frontend
npm install
# Add textbook content to docs/ directory
npm run build
npm run serve  # For local serving
```

### 3. Set up the backend (AI service)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure environment variables
Create `.env` file in backend directory:
```env
OPENAI_API_KEY=your_api_key_here  # Or use local model configuration
QDRANT_URL=your_qdrant_url
NEON_DB_URL=your_neon_db_url
```

### 5. Initialize the vector database
```bash
cd backend
python -m scripts.initialize_embeddings
```

## Running the Application

### Frontend (Textbook)
```bash
cd frontend
npm run start  # Runs Docusaurus development server
```

### Backend (AI Service)
```bash
cd backend
uvicorn src.api.main:app --reload --port 8000
```

## Key Endpoints

### Textbook Content
- `GET /api/textbook` - Get all textbook content
- `GET /api/chapters/{id}` - Get specific chapter
- `GET /api/chapters` - List all chapters

### AI Chatbot
- `POST /api/ai/query` - Submit a question to the AI
- `GET /api/ai/history/{session_id}` - Get conversation history

## Building the Textbook

1. Add your textbook content as markdown files in `docs/textbook/`
2. Update `docusaurus.config.js` with navigation structure
3. Run `npm run build` to generate the static site

## Embedding Management

To update embeddings when textbook content changes:
```bash
cd backend
python -m scripts.update_embeddings
```