# Blackstrap - AI-Powered Reader Plan

**"In honor of the most nutrient-rich variant of molasses"**

## Vision
Anti-technological design that invites deep reading. Serifs, texture, and visual non-sequiturs that cause pause and reflection.

## Progress
- [x] Create project structure
- [x] Create SQLite data models (feeds, articles, narratives, feedback, MCP)
- [x] Set up Flask app with basic routing and configuration  
- [x] Create database initialization and migration utilities
- [x] Build Seeker agent skeleton with static test data
- [x] Build Synthesizer agent with OpenAI integration
- [x] Implement MCP context system with vector embeddings
- [x] Create CLI interface for manual agent runs
- [x] Create templates for feed management (create/edit forms)
- [x] Build narrative viewing interface with feedback collection
- [x] Add synthesis trigger endpoint and progress indication
- [x] Style interface with contemplative, anti-tech design (serifs, texture, visual pauses)
- [x] Wire everything together and test full flow
- [x] Add error handling and validation
- [x] Final testing and documentation

## Architecture
- **Flask app** with SQLite backend
- **Seeker Agent** - fetches article metadata from Scholar/RSS/arXiv
- **Synthesizer Agent** - LLM-powered narrative synthesis
- **Master Context Profile (MCP)** - growing context repository with embeddings
- **Anti-technological UI** - contemplative design encouraging deep reading

## Tech Stack
- Flask + SQLite + OpenAI GPT/Embeddings
- Start simple, scale to FAISS/Chroma later
