from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import json
import os
import PyPDF2
from dotenv import load_dotenv
import openai
import httpx

# Local imports
import models
from database import engine, SessionLocal, Base

# -------------------------
# DB Setup
# -------------------------
Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# LLM Helper Function
# -------------------------
def extract_skills_from_text(text: str) -> list:
    """Uses LLM to extract skills from a given text block."""
    if not openai.api_key:
        print("ERROR: OpenAI API key is not configured in the .env file.")
        return []

    prompt = f"""
    From the following job description or resume text, extract a list of key technical skills, tools, and programming languages.
    Return only a raw JSON array of strings inside a JSON object, like {{"skills": ["Python", "SQL", "Docker"]}}. Do not include markdown formatting.
    Text:
    {text[:2000]}
    """
    try:
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
        )
        skills_text = resp.choices[0].message.content
        data = json.loads(skills_text)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
        
        print(f"LLM WARNING: JSON was returned, but no list of skills was found inside. Response: {skills_text}")
        return []

    except openai.APIAuthenticationError as e:
        print(f"LLM ERROR: OpenAI API authentication failed. Check your API key. Details: {e}")
        return []
    except Exception as e:
        print(f"LLM ERROR: An unexpected error occurred: {e}")
        return []

# -------------------------
# Database Population Logic
# -------------------------
def populate_jobs_db(db: Session):
    """Checks if the jobs table is empty and populates it, including LLM-extracted skills."""
    if db.query(models.Job).count() == 0:
        print("Jobs table is empty. Populating from API and extracting skills...")
        try:
            response = httpx.get("https://jsonplaceholder.typicode.com/posts")
            response.raise_for_status()
            jobs_data = response.json()
            skill_sets = [
                ["Python", "FastAPI", "SQL", "Docker"],
                ["JavaScript", "React", "Node.js", "CSS"],
                ["Java", "Spring Boot", "Maven", "PostgreSQL"],
                ["Go", "Gin", "Kubernetes", "gRPC"],
            ]
            for i, job_data in enumerate(jobs_data):
                description = job_data["body"]
                skills_to_inject = skill_sets[i % len(skill_sets)]
                enhanced_description = f"This is a job for a software developer. Required skills: {', '.join(skills_to_inject)}. Original post: {description}"
                skills = extract_skills_from_text(enhanced_description)
                print(f"Extracted skills for job {job_data['id']}: {skills}")
                job = models.Job(id=job_data["id"], title=job_data["title"], description=description, skills=json.dumps(skills))
                db.add(job)
            db.commit()
            print("Successfully populated jobs table.")
        except Exception as e:
            print(f"Error populating jobs table: {e}")
            db.rollback()
    else:
        print("Jobs table already contains data. Skipping population.")

# -------------------------
# Lifespan Event Handler
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    db = SessionLocal()
    populate_jobs_db(db)
    db.close()
    yield
    print("Application shutdown...")

# -------------------------
# App Init
# -------------------------
app = FastAPI(title="Job Portal Backend", lifespan=lifespan)

# -------------------------
# CORS Middleware
# -------------------------
origins = ["http://localhost:3000", "http://localhost:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Environment Variables
# -------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# =========================
# API ENDPOINTS
# =========================
@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return [{"id": job.id, "title": job.title, "description": job.description, "skills": json.loads(job.skills)} for job in jobs]

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        reader = PyPDF2.PdfReader(file.file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
    candidate = models.Candidate(name=file.filename, resume_text=text, skills=json.dumps([]))
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return {"candidate_id": candidate.id, "name": candidate.name, "resume_text": candidate.resume_text[:500] + "..."}

@app.post("/analyze_resume/{candidate_id}")
def analyze_resume(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=400, detail="No resume text available for analysis.")
    skills = extract_skills_from_text(candidate.resume_text)
    candidate.skills = json.dumps(skills)
    db.commit()
    db.refresh(candidate)
    return {"candidate_id": candidate.id, "name": candidate.name, "resume_text_preview": candidate.resume_text[:500] + "...", "skills": skills}

@app.post("/candidates/{candidate_id}/generate-matches")
def generate_matches(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate_skills = set(json.loads(candidate.skills))
    if not candidate_skills:
        raise HTTPException(status_code=400, detail="Candidate has no skills to match.")
    db.query(models.Match).filter(models.Match.candidate_id == candidate_id).delete()
    db.commit()
    jobs = db.query(models.Job).all()
    for job in jobs:
        job_skills = set(json.loads(job.skills))
        if not job_skills: continue
        matched_skills = list(candidate_skills.intersection(job_skills))
        missing_skills = list(job_skills.difference(candidate_skills))
        score = round((len(matched_skills) / len(job_skills)) * 100) if len(job_skills) > 0 else 0
        if score > 20:
            new_match = models.Match(candidate_id=candidate_id, job_id=job.id, score=score, matched_skills=json.dumps(matched_skills), missing_skills=json.dumps(missing_skills))
            db.add(new_match)
    db.commit()
    return {"status": "complete", "message": "Matches have been generated and saved."}

@app.get("/candidates/{candidate_id}/matches")
def get_saved_matches(candidate_id: int, db: Session = Depends(get_db)):
    print(f"\n--- [DEBUG] Searching for matches for Candidate ID: {candidate_id} ---")
    
    try:
        results = db.query(models.Match, models.Job)\
                    .join(models.Job, models.Match.job_id == models.Job.id)\
                    .filter(models.Match.candidate_id == candidate_id)\
                    .order_by(models.Match.score.desc())\
                    .all()
        
        print(f"--- [DEBUG] Database query found {len(results)} matches. ---")

        matches_list = []
        for match, job in results:
            matches_list.append({
                "job_id": match.job_id,
                "job_title": job.title,
                "score": match.score,
                "matched_skills": json.loads(match.matched_skills),
                "missing_skills": json.loads(match.missing_skills)
            })
        
        print(f"--- [DEBUG] Successfully formatted and returning {len(matches_list)} matches. ---\n")
        return matches_list
    
    except Exception as e:
        print(f"\n!!! [DEBUG] DATABASE ERROR in get_saved_matches: {e} !!!\n")
        # We raise an HTTPException to ensure a proper error response is sent
        raise HTTPException(status_code=500, detail="An internal error occurred while fetching matches.")