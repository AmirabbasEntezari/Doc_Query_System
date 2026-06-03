# 📄 Smart Document Q&A System (RAG-based)

This project is an intelligent **Retrieval-Augmented Generation (RAG)** system that allows users to upload Microsoft Word documents (`.docx`), extract their text contents automatically, and query them using an advanced, customized Django Admin interface. The AI automatically retrieves the most relevant text chunks, provides a precise response in Persian, and extracts topical tags from the conversation.

---

## ✨ Key Features

* **Hybrid Querying Scope:** Supports querying either a single specific document or searching globally across all uploaded documents.
* **Smart Source Tracking:** In global search mode, the LLM intelligently determines which document contains the answer and extracts its ID. The system then automatically links the chat session to that specific document in the database for perfect filtering.
* **Automated Topical Tagging:** Dynamically extracts 1 to 3 relevant Persian keywords from the conversation context while filtering out duplicate or filename-based tags to keep the taxonomy clean.
* **Anti-Lock Database Architecture:** Decouples heavy AI network requests from Django database transactions, completely preventing the notorious SQLite `database is locked` error.
* **Optimized File & DB Management:** Separates uploaded text files into a clean `media/documents/` path and isolates the SQLite database within a dedicated `db_volume/` directory to eliminate Windows-to-Docker permission conflicts.
* **Full Containerization:** Ready for rapid development and production deployment using optimized Docker and Docker Compose configurations with persistent named volumes.

---

## 🛠 Tech Stack & Tools

* **Backend Framework:** Django 4.2+ (Highly Customized Admin Panel)
* **LLM Orchestration:** LangChain / LangChain OpenAI
* **AI Provider:** OpenRouter API (Default optimized model: `google/gemini-2.5-flash:free`)
* **Text Processing:** docx2txt & RecursiveCharacterTextSplitter
* **Containerization:** Docker & Docker Compose
* **Database:** SQLite 3 (Multi-environment configuration)

---

## 📂 Project Directory Structure

```text
document_qa_project/
│
├── core/                   # Main Django project settings
│   ├── settings.py         # Multi-environment database and Media configuration
│   ├── urls.py             # Global routing for Admin, API, and Media files
│   └── .env                # Protected environment variables & API Key
│
├── documents/              # Core application for document processing and QA
│   ├── admin.py            # Optimized, non-blocking admin configurations
│   ├── models.py           # Database models for Document, ChatSession, and Tag
│   └── services.py         # Text extraction, RAG chunking, and LLM orchestration
│
├── db_volume/              # Isolated directory protecting the SQLite database
│   └── db.sqlite3
│
├── media/                  # Storage directory for uploaded .docx files
│   └── documents/
│
├── Dockerfile              # Tailored system image with permission optimizations
├── docker-compose.yml      # Orchestrates named volumes and web services
├── manage.py
└── requirements.txt        # Python package dependencies


---
## 🚀 Installation & Setup

The project can be executed using either Docker (recommended) or a local Python environment.

---

# Option A — Docker Setup (Recommended)

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/document_qa_project.git
cd document_qa_project
```

---

## 2. Configure Environment Variables

Create a `.env` file inside the `core/` directory:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

OPENROUTER_API_KEY=your-openrouter-api-key

DB_NAME=db.sqlite3
```

Replace `your-openrouter-api-key` with your actual OpenRouter API key.

---

## 3. Build and Start the Containers

Build the Docker image and start all services:

```bash
docker compose up --build
```

Or run in detached mode:

```bash
docker compose up -d --build
```

> **Note:** Database migrations are automatically executed during container startup through the Docker Compose configuration. No manual migration step is required.

---

## 4. Create an Admin User

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts to create your administrator account.

---

## 5. Access the Application

Open your browser:

```text
http://localhost:8000/admin/
```

Log in using the superuser credentials created above.

---

# Option B — Local Development Setup

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/document_qa_project.git
cd document_qa_project
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv env
source env/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file inside the `core/` directory:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

OPENROUTER_API_KEY=your-openrouter-api-key

DB_NAME=db.sqlite3
```

---

## 5. Apply Database Migrations

For local execution, migrations must be applied manually:

```bash
python manage.py migrate
```

---

## 6. Create a Superuser

```bash
python manage.py createsuperuser
```

---

## 7. Run the Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

---

# 📄 Upload Documents

1. Open the Django Admin Panel.
2. Navigate to **Documents**.
3. Upload one or more `.docx` files.
4. The system automatically extracts and processes document content for retrieval and question answering.

---

# 💬 Querying Documents

Users can create chat sessions and ask questions about:

* A specific uploaded document.
* All uploaded documents (global search mode).

The system automatically:

* Retrieves the most relevant text chunks.
* Generates a Persian response using the configured LLM.
* Detects the source document when operating in global mode.
* Associates the chat session with the detected document.
* Extracts meaningful topical tags from the conversation.

---

# 🐳 Persistent Storage

The project uses dedicated storage locations for uploaded files and database persistence:

```text
media/
└── documents/

db_volume/
└── db.sqlite3
```

This separation prevents file permission conflicts and ensures data remains available across container rebuilds and application restarts.

---

# 🛑 Stopping the Application

### Docker

```bash
docker compose down
```

Remove containers and volumes:

```bash
docker compose down -v
```

### Local Environment

Press:

```text
CTRL + C
```

inside the terminal running the Django development server.
