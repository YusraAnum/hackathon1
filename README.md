# AI-Native Textbook with AI Chatbot

This project implements a web-based AI-native textbook with integrated AI chatbot functionality that answers questions based only on textbook content.

## Prerequisites

- Node.js 18+
- Python 3.11+
- Git

## Project Structure

```
backend/          # FastAPI backend for AI services and textbook API
├── src/
│   ├── models/          # Data models
│   ├── services/        # Business logic services
│   ├── api/            # API routes
│   └── utils/          # Utility functions
├── tests/              # Backend tests
└── requirements.txt    # Python dependencies

frontend/         # Docusaurus-based textbook frontend
├── src/               # Frontend components and services
├── static/           # Static assets
├── tests/            # Frontend tests
└── package.json      # Node.js dependencies

docs/             # Textbook content and Docusaurus config
├── textbook/         # Markdown files for textbook content
├── docusaurus.config.js
└── sidebars.js
```

## Setup Instructions

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
- `GET /api/textbook/chapters` - Get all textbook chapters
- `GET /api/textbook/chapters/{id}` - Get specific chapter
- `GET /api/textbook/chapters/{id}/toc` - Get chapter table of contents

### AI Chatbot
- `POST /api/ai/query` - Submit a question to the AI
- `POST /api/ai/validate` - Validate if question can be answered from textbook
- `GET /api/ai/sessions/{session_id}` - Get conversation history

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

## Development Workflow

1. Frontend changes can be developed with hot reloading using `npm run start`
2. Backend changes require restarting the FastAPI server when using `--reload` flag
3. Both services should be running simultaneously for full functionality
4. Use the API contracts in `specs/001-textbook-generation/contracts/` as reference for integration