# 🎓 AI Study Partner & Advisor Matcher

**An intelligent, multi-agent AI companion for studying, research, and academic advisor discovery.**

This project is a **Full-Stack Agentic AI System** built with **LangGraph**, **FastAPI**, and **Ollama (Local LLMs)**.  
It goes beyond traditional RAG by utilizing **task-specialized agents** that can tutor, quiz, research, and match your research ideas to real professors at **NCKU CSIE** using a dedicated vector database.

---

## ✨ Key Features

### 🧠 Intelligent Study Tools
- **Feynman Simplifier**  
  Explains complex concepts using simple language and analogies.  
  *Example: “Explain Transformers like I’m 5.”*

- **Document Q&A (RAG)**  
  Chat with your lecture slides, papers, or notes (PDF).

- **Auto Quiz Generator**  
  Generates quizzes from uploaded PDFs and grades your answers automatically.

- **Deep Research Mode**  
  Falls back to web search (Google / Tavily) when information is not found in documents.

### 🏫 Academic Advisor Matcher (NCKU CSIE)
- **Supervisor Discovery**  
  Describe your research idea and get matched with the most relevant professor.

- **Permanent Faculty Knowledge Base**  
  Uses a dedicated vector database built from scraped NCKU CSIE faculty data.

- **Email Drafting Agent**  
  Automatically generates professional emails to contact the recommended advisor.

---

## ⚡ System Architecture

### 🧩 Agentic Design with LangGraph

The system uses **LangGraph** to orchestrate multiple specialized agents. An **intent classifier** routes user requests to the appropriate agent:

| Agent | Responsibility | Example Use Case |
|-------|----------------|----------------|
| **Tutor Agent** | Explains and simplifies complex concepts using analogies or plain language | “Explain Transformers like I’m 5.” |
| **Quiz Agent** | Generates quizzes from uploaded PDFs, collects answers, and automatically grades them | “Give me a quiz on this lecture slide.” |
| **Advisor Agent** | Matches your research ideas to relevant NCKU CSIE professors and drafts contact emails | “I want to do a project on blockchain for supply chains. Who should I work with?” |
| **Query Agent (RAG)** | Answers questions from user-uploaded documents or lecture notes | “What is the main formula on page 5 of this PDF?” |
| **Summarizer Agent** | Summarizes PDFs or lecture slides into concise notes | “Summarize this document in 3 key points.” |
| **Feynman Simplifier Node** | Uses the Feynman technique to explain any topic in simple terms | “Explain Recurrent Neural Networks like I’m 5.” |

> The **intent classifier** detects the user’s request type (study, quiz, research, or advisor matching) and routes it to the proper agent.  
> Each agent accesses either the **user ephemeral vector store** (`chroma_db_user`) or the **permanent faculty vector store** (`chroma_db_faculty`) depending on the task.

---

### 🧠 Dual-Memory Vector System

| Memory Type | Purpose | Persistence |
|------------|---------|-------------|
| `chroma_db_user` | User-uploaded PDFs | ❌ Ephemeral |
| `chroma_db_faculty` | NCKU faculty data | ✅ Permanent |

- **User data** is wiped when switching chats to ensure privacy.
- **Faculty database** is built once and reused indefinitely.

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, LangChain, LangGraph  
- **LLMs & Embeddings:** Ollama (Llama3 / Mistral / Gemma), `nomic-embed-text`  
- **Frontend:** React, Tailwind CSS, Lucide Icons  
- **Vector Database:** ChromaDB (Local)  
- **Tools:** SerpAPI / Tavily (Web Search), BeautifulSoup (Scraping)

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10+**
- Node.js & npm
- **Ollama** running locally

```bash
ollama serve
ollama pull nomic-embed-text
ollama pull llama3
```

## 🔧 Backend Setup

```bash
git clone https://github.com/Kilaysz/Study-Helper.git
cd Study-Helper

# Create venv and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```


## 2. Environment Variables
Create a .env file in the project root:

```bash
SERPAPI_API_KEY=your_serpapi_key_here
TAVILY_API_KEY=your_tavily_key_here
OLLAMA_LOCAL_URL=http://localhost:11434
```

## 3. Start Server

```bash
./run.ps1
```

### ⚠️ On first run, the server will automatically scrape the NCKU CSIE faculty website and build the professor vector database.

### 🎨 Frontend Setup
```bash
Copy code
cd frontend
npm install
npm run dev
Access the app at:
👉 http://localhost:5173
```

### 📖 How to Use
## Mode 1: Study & Summarize
Upload a PDF (slides, papers, notes)
Ask:
```bash
“Summarize this document”
“What is the main formula on page 5?”
```

## Mode 2: Feynman Technique
Ask:

```bash Explain Recurrent Neural Networks like I’m 5.```
## Mode 3: Advisor Matcher
No upload required.
Ask:
```bash
I want to do a project on blockchain for supply chains.
Who should I work with?
✔ Finds the best matching professor
✔ Drafts a professional contact email
✔ Verifies missing info via web search if needed
```

## Mode 4: Quiz Mode
Upload a PDF

Ask:
```bash
Give me a quiz on this document.
```
```bash
Answer:
1. A
2. C
3. B
```
Get instant grading & feedback after answering
### 📂 Project Structure
```bash
├── uv.lock
├── DAG.png
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── run.ps1                   # Server startup script
├── server.py                 # FastAPI backend entry point
├── data/                   # Scraped professors.json (Permanent)
├── uploads/                # Temporary user PDFs
├── chroma_db_faculty/      # Faculty Vector DB (Permanent)
├── chroma_db_user/         # User Vector DB (Ephemeral)
├── frontend/                 # React Frontend
│   ├── package.json
│   ├── run.ps1               # Frontend startup script
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx           # Main React App component
│       ├── main.jsx          # Entry point
│       └── components/
│           ├── ChatArea.jsx  # Chat interface component
│           └── Sidebar.jsx   # Sidebar navigation component
├──src/                      # Backend Source Code
    ├── graph.py              # LangGraph workflow & edge definitions
    ├── state.py              # AgentState schema definition
    ├── tools.py              # External tool definitions
    ├── nodes/                # Agent Logic Nodes
    │   ├── classifier.py     # Intent classification node
    │   ├── query.py          # RAG & Q/A node
    │   ├── quiz.py           # Quiz generation node
    │   ├── router.py         # Routing decision logic
    │   ├── simplifier.py     # Feynman simplifier node
    │   ├── summarizer.py     # Document summarization node
    │   └── advisor.py        # Advisor Recommendation mode
    └── utils/                # Utilities
        ├── llm_setup.py      # LLM initialization & config
        ├── pdf_loader.py     # PDF parsing & text extraction
        ├── scrape_professors.py    # Faculty scraper
        └── vector_store.py # Chunking and Vector DB storing
```

### DAG
![System Architecture](./DAG.png)

### 🛡️ License
Distributed under the MIT License.
See LICENSE for details.

## 🤝 Contributing
Fork the repository

## Create a feature branch
```bash
git checkout -b feature/AmazingFeature
```
Commit your changes
Push to your branch
Open a Pull Request

## ⭐ Acknowledgements
LangChain & LangGraph
Ollama
ChromaDB
NCKU CSIE Faculty