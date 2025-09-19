## LLM-Powered Job Portal

A web application that uses a Large Language Model (LLM) to analyze resumes, extract skills, and match candidates with suitable job listings.

# Tech Stack

    Frontend: Next.js (React), Tailwind CSS

    Backend: FastAPI (Python), SQLAlchemy

    Database: SQLite

    LLM: OpenAI API

    Containerization: Docker, Docker Compose

# Setup and Installation

1. Clone the repository:
Bash

git clone <your-repository-url>
cd <your-repository-name>

2. Set up your API Key:

    Create a file named .env inside the backend directory.

    Add your OpenAI API key to this file:

    OPENAI_API_KEY="sk-..."

Running the Application 🚀

You have two options for running this project. The Docker method is recommended for its simplicity.

Option 1: Running with Docker Compose (Recommended)

This method builds and runs both the frontend and backend services in containers with a single command.

Prerequisites:

    Docker & Docker Compose

Instructions:

    From the project's root directory, run the following command:
    Bash

    docker-compose up --build

    Open your browser and go to http://localhost:3001 to use the application.

To stop the application, press CTRL+C in the terminal, then run docker-compose down.

Option 2: Running Locally (Manual Setup)

This method requires running the backend and frontend in two separate terminals.

Prerequisites:

    Python 3.11+

    Node.js & npm

Terminal 1: Start the Backend
Bash

# Navigate to the backend folder
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# .\venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload

Terminal 2: Start the Frontend
Bash

# Navigate to the frontend folder
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev

Open your browser and go to http://localhost:3001 to use the application.