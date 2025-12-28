# 🎓 AI Study Partner & Advisor Matcher

**An intelligent AI companion for studying, research, and academic advisor discovery.**

This project is a **Full-Stack Agentic AI System** built with **LangGraph**, **FastAPI**, and **Ollama (Local LLMs)**.  
It goes beyond traditional RAG by using **task-specialized agents** that can tutor, quiz, research, and even **match your research idea to real professors at NCKU CSIE** using a dedicated vector database.

---

## ✨ Key Features

### 🧠 Intelligent Study Tools
- **Feynman Simplifier**  
  Explains complex concepts using simple language and analogies  
  _Example: “Explain Transformers like I’m 5.”_

- **Document Q&A (RAG)**  
  Chat with your lecture slides, papers, or notes (PDF).

- **Auto Quiz Generator**  
  Generates quizzes from uploaded PDFs and grades your answers automatically.

- **Deep Research Mode**  
  Falls back to web search (Google / Tavily) when information is not found in documents.

---

### 🏫 Academic Advisor Matcher (NCKU CSIE)
- **Supervisor Discovery**  
  Describe your research idea and get matched with the most relevant professor.

- **Permanent Faculty Knowledge Base**  
  Uses a dedicated vector database built from scraped NCKU CSIE faculty data.

- **Email Drafting Agent**  
  Automatically generates a professional email to contact the recommended advisor.

---

## ⚡ System Architecture

### 🧩 Agentic Design with LangGraph
An intent classifier routes user requests to specialized agents:

- **Tutor Agent** → explanation & simplification  
- **Quiz Agent** → quiz creation & grading  
- **Advisor Agent** → supervisor matching  
- **Query Agent** → document Q&A (RAG)

---

### 🧠 Dual-Memory Vector System

| Memory Type | Purpose | Persistence |
|------------|--------|------------|
| `chroma_db_user` | User-uploaded PDFs | ❌ Ephemeral |
| `chroma_db_faculty` | NCKU faculty data | ✅ Permanent |

- User data is **wiped when switching chats** → privacy-safe  
- Faculty database is **built once and reused forever**

---

## 🛠️ Tech Stack

**Backend**
- Python
- FastAPI
- LangChain
- LangGraph

**LLMs & Embeddings**
- Ollama (Llama3 / Mistral / Gemma)
- nomic-embed-text

**Frontend**
- React
- Tailwind CSS
- Lucide Icons

**Vector Database**
- ChromaDB (Local)

**Tools**
- SerpAPI / Tavily (Web Search)
- BeautifulSoup (Scraping)

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
🔧 Backend Setup
bash
Copy code
git clone https://github.com/yourusername/study-partner.git
cd study-partner

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
Environment Variables
Create a .env file in the project root:

env
Copy code
SERPAPI_API_KEY=your_serpapi_key_here
TAVILY_API_KEY=your_tavily_key_here
OLLAMA_LOCAL_URL=http://localhost:11434
Start Backend Server
bash
Copy code
python server.py
⚠️ On first run, the server will automatically scrape the NCKU CSIE faculty website and build the professor vector database.

🎨 Frontend Setup
bash
Copy code
cd frontend
npm install
npm run dev
Access the app at:
👉 http://localhost:5173

📖 How to Use
Mode 1: Study & Summarize
Upload a PDF (slides, papers, notes)

Ask:

“Summarize this document”

“What is the main formula on page 5?”

Mode 2: Feynman Technique
Ask:

text
Copy code
Explain Recurrent Neural Networks like I’m 5.
Mode 3: Advisor Matcher
No upload required.

Ask:

text
Copy code
I want to do a project on blockchain for supply chains.
Who should I work with?
✔ Finds the best matching professor
✔ Drafts a professional contact email
✔ Verifies missing info via web search if needed

Mode 4: Quiz Mode
Upload a PDF

Ask:

text
Copy code
Give me a quiz on this document.
Answer:

text
Copy code
1. A
2. C
3. B
Get instant grading & feedback

📂 Project Structure
plaintext
Copy code
├── data/                   # Scraped professors.json (Permanent)
├── uploads/                # Temporary user PDFs
├── chroma_db_faculty/      # Faculty Vector DB (Permanent)
├── chroma_db_user/         # User Vector DB (Ephemeral)
├── frontend/               # React Frontend
├── src/
│   ├── graph.py            # LangGraph workflow
│   ├── state.py            # Agent state schema
│   ├── tools.py            # Web search & utilities
│   ├── nodes/
│   │   ├── advisor.py      # Supervisor matching logic
│   │   ├── classifier.py   # Intent router
│   │   ├── query.py        # RAG Q&A
│   │   ├── simplifier.py   # Feynman explanations
│   │   └── quiz.py
│   └── utils/
│       ├── vector_store.py # Dual-DB management
│       └── pdf_loader.py   # PDF parsing
├── scrape_professors.py    # Faculty scraper
└── server.py               # FastAPI entry point
🛡️ License
Distributed under the MIT License.
See LICENSE for details.

🤝 Contributing
Fork the repository

Create a feature branch

bash
Copy code
git checkout -b feature/AmazingFeature
Commit your changes

Push to your branch

Open a Pull Request

⭐ Acknowledgements
LangChain & LangGraph

Ollama

ChromaDB

NCKU CSIE Faculty

yaml
Copy code

---

If you want next:
- 📊 **System architecture diagram**
- 🧪 **Evaluation / benchmarking section**
- 🎓 **Academic-style abstract**
- 🌟 **GitHub badges & shields**

Just tell me — this README is already **portfolio-grade** 💯