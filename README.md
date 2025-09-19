# LLM-Powered Job Portal

A web application that uses a Large Language Model (LLM) to analyze resumes, extract skills, and match candidates with suitable job listings.

## Tech Stack

- **Frontend:** Next.js (React), Tailwind CSS  
- **Backend:** FastAPI (Python), SQLAlchemy  
- **Database:** SQLite  
- **LLM:** OpenAI API  
- **Containerization:** Docker, Docker Compose  

---

## Getting Started

### Prerequisites

- Python **3.11+**  
- Node.js & npm  
- Docker & Docker Compose  

---

### Initial Setup

Clone the repository:

```bash
git clone https://github.com/Aza3l01/hackathon-project
cd hackathon-project
```

Set up the OpenAI API Key:

1. Create a file named `.env` inside the `backend` directory.  
2. Add your API key to this file:  

```env
OPENAI_API_KEY="sk-..."
```

---

## Running the Application

This project can be run using **Docker Compose** (recommended) or manually.  

---

### Option 1: Docker Compose (Recommended)

Build and run the entire application with a single command:

```bash
docker-compose up --build
```

Access the application at:  [http://localhost:3001](http://localhost:3001)

To stop the application:

```bash
CTRL+C
docker-compose down
```

---

### Option 2: Run Locally (Manual)

Run the backend and frontend in two separate terminals.  

#### Terminal 1: Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # On macOS/Linux
# .\venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

#### Terminal 2: Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend server
npm run dev
```

Access the application at:  [http://localhost:3001](http://localhost:3001)