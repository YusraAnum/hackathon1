# Implementation Plan: AI-Native Textbook with AI Chatbot

**Branch**: `001-textbook-generation` | **Date**: 2025-12-08 | **Spec**: [specs/001-textbook-generation/spec.md]
**Input**: Feature specification from `/specs/001-textbook-generation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a web-based AI-native textbook with integrated AI chatbot that answers questions based only on textbook content. The system will use Docusaurus for the textbook interface with an AI backend using vector databases for RAG functionality. The architecture prioritizes simplicity, lightweight design, and free-tier compatibility to ensure accessibility.

## Technical Context

**Language/Version**: JavaScript/TypeScript (Node.js 18+), Python 3.11 for AI backend
**Primary Dependencies**: Docusaurus, FastAPI, Qdrant, Neon, OpenAI API or compatible alternative
**Storage**: Vector database (Qdrant) for embeddings, Neon (PostgreSQL) for metadata
**Testing**: Jest for frontend, pytest for backend, Playwright for E2E
**Target Platform**: Web application (browser-based textbook with cloud backend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <3s page load time, <10s AI response time, 99% uptime
**Constraints**: Free-tier resource limits, lightweight embeddings, <100 concurrent users initially
**Scale/Scope**: 6 textbook chapters, 1000+ students, 100K+ embedding vectors

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Simplicity Over Complexity**: Architecture must avoid over-engineering - use minimal components necessary
2. **Free-Tier Compatibility**: All technical choices must work within free-tier constraints
3. **Lightweight Design**: System architecture must prioritize minimal resource usage
4. **RAG Integrity**: AI responses must be sourced ONLY from textbook content
5. **Consistency Across Content**: UI/UX patterns must be consistent across all textbook chapters

All constitution principles must be validated during design phase. Any violations require explicit justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-textbook-generation/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── textbook_content.py
│   │   ├── ai_query.py
│   │   └── user_session.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── embedding_service.py
│   │   ├── content_service.py
│   │   └── rag_service.py
│   ├── api/
│   │   ├── textbook_routes.py
│   │   ├── ai_routes.py
│   │   └── main.py
│   └── utils/
│       ├── text_processor.py
│       └── validation.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── TextbookViewer.jsx
│   │   ├── AIChatbot.jsx
│   │   ├── Navigation.jsx
│   │   └── TranslationControls.jsx
│   ├── pages/
│   │   ├── ChapterPage.jsx
│   │   ├── HomePage.jsx
│   │   └── ChatPage.jsx
│   └── services/
│       ├── api_client.js
│       └── content_loader.js
├── static/
│   └── textbook-content/
│       ├── chapter-1/
│       ├── chapter-2/
│       └── ...
└── tests/
    ├── unit/
    └── e2e/

docs/
├── textbook/
│   ├── intro-to-physical-ai.md
│   ├── basics-humanoid-robotics.md
│   ├── ros2-fundamentals.md
│   ├── digital-twin-simulation.md
│   ├── vision-language-action.md
│   └── capstone-project.md
└── docusaurus.config.js
```

**Structure Decision**: Web application with separate backend (FastAPI) and frontend (Docusaurus-based) to allow independent scaling and development. The textbook content is stored separately in the docs directory and built by Docusaurus, while the AI backend handles RAG functionality and user interactions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [N/A] | [No violations identified] | [Architecture aligns with constitution] |
