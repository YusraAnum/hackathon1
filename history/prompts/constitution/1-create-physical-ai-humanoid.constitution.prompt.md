---
id: 1
title: Create Physical AI Humanoid Constitution
stage: constitution
date: 2025-12-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Claude Code
command: /sp.constitution
labels: [constitution,physical-ai,humanoid-robotics,setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Project Name: Physical AI & Humanoid Robotics

Purpose: Create a short, clean, professional AI-Native textbook based on the Physical AI & Humanoid Robotics course. The book must serve as a fast, simple, high-quality learning resource that works perfectly with a built-in RAG chatbot and modern Docusaurus UI.

Scope:

Book will contain 6 short, focused chapters:
Introduction to Physical AI
Basics of Humanoid Robotics
ROS 2 Fundamentals
Digital Twin Simulation (Gazebo + Isaac)
Vision-Language-Action Systems
Capstone: Simple AI-Robot Pipeline
Content must stay concise, accurate, and easy to understand.
UI must be clean, modern, minimal, and fast.
Core Principles:
Simplicity over complexity.
Content must be correct, structured, and minimal.
Free-tier-compatible architecture for embeddings and API usage.
Avoid heavy GPU steps; prioritize lightweight design.
RAG chatbot answers ONLY from book text.
Consistent writing style and formatting across chapters.
Fast build, clean structure, and production-safe code.
Key Features:

Docusaurus-based textbook with clean layout.
Integrated RAG chatbot (Qdrant + Neon + FastAPI).
"Select text → Ask AI" interaction.
Ready structure for:
Personalize Chapter button
Urdu Translation button
User profile–based content (optional)
Constraints:

Minimal compute usage.
Lightweight embeddings (for free tiers).
Keep chapter size small and clean.
Success Criteria:

Book builds successfully with no issues.
RAG chatbot returns accurate answers from book content.
UI looks clean, modern, and professional.
Chapters are short, well-formatted, and aligned with course outcomes.
Project deploys smoothly to GitHub Pages.
Generate the complete constitution.

## Response snapshot

Created the complete constitution for the Physical AI & Humanoid Robotics textbook project based on the provided requirements. The constitution includes:

Core Principles:
- Simplicity Over Complexity
- Content Accuracy and Structure
- Free-Tier Compatibility
- Lightweight Design
- RAG Integrity
- Consistency Across Content

Technical Requirements:
- Docusaurus Implementation
- RAG Chatbot Integration
- Feature Readiness

Development Workflow:
- Minimal Compute Usage
- Lightweight Embeddings
- Clean Chapter Structure

The constitution establishes governance rules and is versioned as 1.0.0, ratified on 2025-12-08.

## Outcome

- ✅ Impact: Complete project constitution created with all required principles
- 🧪 Tests: No tests needed for constitution creation
- 📁 Files: Updated .specify/memory/constitution.md with complete constitution
- 🔁 Next prompts: Plan feature specifications based on constitution
- 🧠 Reflection: Constitution aligns with all specified project requirements and principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin feature specification based on constitution