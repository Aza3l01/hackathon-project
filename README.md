LLM-Powered Job Portal

A web application that uses a Large Language Model (LLM) to analyze resumes, extract skills, and match candidates with suitable job listings.

Tech Stack

    Frontend: Next.js (React), Tailwind CSS

    Backend: FastAPI (Python), SQLAlchemy

    Database: SQLite

    LLM: OpenAI API

    Containerization: Docker, Docker Compose

Getting Started

Prerequisites

    Python 3.11+

    Node.js & npm

    Docker & Docker Compose

Initial Setup

    Clone the repository:

    git clone https://github.com/Aza3l01/hackathon-project
    cd hackathon-project

    Set up the OpenAI API Key:

        Create a file named .env inside the backend directory.

        Add your API key to this file:

        OPENAI_API_KEY="sk-..."

Running the Application

This project can be run using Docker Compose or manually. The Docker method is recommended for a simpler setup.

Option 1: Docker Compose (Recommended)

This method builds and runs the entire application with a single command.

    From the project's root directory, run the build command:

    docker-compose up --build

    Access the application in your browser at http://localhost:3001.

To stop the application, press CTRL+C in the terminal and then run:

docker-compose down

Option 2: Locally (Manual)

This method requires running the backend and frontend in two separate terminals.

Terminal 1: Start the Backend

# Navigate to the backend directory
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

# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev

Access the application in your browser at http://localhost:3001.