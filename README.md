🎓 AI Study Partner Agent

A Full-Stack AI Application built with LangGraph, FastAPI, and React that acts as an intelligent study assistant. It supports multi-modal interactions including RAG-based quizzes, document summarization, and web-grounded research.

✨ Features

🧠 Intelligent Routing: Automatically classifies user intent to switch between modes (Summary, Quiz, Query, Simplify).

📚 RAG (Retrieval Augmented Generation): Upload PDFs to chat with your documents using Vector Search (ChromaDB).

⚡ Web Search: Integrated with Tavily/DuckDuckGo for real-time internet research.

📝 Interactive Quizzes: Generates questions from your notes and grades your answers instantly.

💡 Feynman Simplifier: Explains complex topics using simple analogies.

💬 Multi-Session Chat: Save and manage multiple conversation histories via a Gemini-style sidebar.

🏗️ Architecture

This project follows a Client-Server architecture with an Agentic backend.

Frontend: React (Vite) + Tailwind CSS

Backend: FastAPI (Python)

Agent Orchestration: LangGraph (Stateful Multi-Actor Graph)

LLM Provider: Ollama (Local) or API Gateway

Vector DB: ChromaDB (In-memory/Persisted)

Directory Structure

study-partner-agent/
├── server.py               # FastAPI Entry Point
├── frontend/               # React Application
└── src/                    # AI Logic
    ├── graph.py            # LangGraph Wiring
    ├── nodes/              # Individual Agents (Quiz, Query, Summarize...)
    └── utils/              # PDF Loader, Vector Store, LLM Setup


🚀 Getting Started

Prerequisites

Python 3.10+ (Recommend using uv for package management)

Node.js 18+

Ollama installed and running (ollama serve)

1. Backend Setup

Clone the repository:

git clone [https://github.com/yourusername/study-partner-agent.git](https://github.com/yourusername/study-partner-agent.git)
cd study-partner-agent


Install Python dependencies:

# Using uv (Recommended)
uv add fastapi uvicorn langchain langgraph langchain-community langchain-chroma pymupdf4llm python-multipart python-dotenv

# OR using pip
pip install -r requirements.txt


Configure Environment Variables:
Create a .env file in the root directory:

# LLM Settings
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3"

# Optional API Keys
TAVILY_API_KEY="tvly-..."


Start the Backend Server:

uv run python server.py


Server will run at http://localhost:8000

2. Frontend Setup

Navigate to the frontend folder:

cd frontend


Install Node dependencies:

npm install


Start the React Dev Server:

npm run dev


App will run at http://localhost:5173

💡 Usage Guide

Upload: Click the "Upload PDF" area in the sidebar to load your lecture notes or papers.

Auto-Detect: Just ask a question!

"Summarize this file" -> Triggers Summarizer Agent.

"Test me on Chapter 3" -> Triggers Quiz Agent.

"Explain Quantum Physics like I'm 5" -> Triggers Simplifier Agent.

"Who won the 2024 World Cup?" -> Triggers Web Search Agent.

Quiz Mode: When in a quiz, answer the question. The agent will automatically grade you and offer another question.

🛠️ Tech Stack Details

LangGraph: Manages the cyclic workflow (e.g., Quiz -> Wait for User -> Grade -> Repeat).

ChromaDB: Indexes PDF chunks for semantic retrieval during quizzes.

PyMuPDF4LLM: Converts PDFs into clean Markdown for better LLM comprehension.

Lucide React: Provides the modern icon set used in the UI.

🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any bugs or feature enhancements.

📄 License

This