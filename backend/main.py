from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import json
import os
import PyPDF2
from dotenv import load_dotenv
import openai

# local imports
import models
from database import engine, SessionLocal, Base

# -------------------------
# DB Setup
# -------------------------
Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# App Init
# -------------------------
app = FastAPI(title="Job Portal Backend")

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# -------------------------
# Health Check
# -------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}


# -------------------------
# Jobs (list only for now)
# -------------------------
@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return jobs


# -------------------------
# Resume Upload
# -------------------------
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    candidate = models.Candidate(
        name=file.filename, resume_text=text, skills=json.dumps([])
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {
        "candidate_id": candidate.id,
        "name": candidate.name,
        "resume_text": candidate.resume_text[:500] + "..."  # preview
    }


# -------------------------
# Analyze Resume with LLM
# -------------------------
@app.post("/analyze_resume/{candidate_id}")
def analyze_resume(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not candidate.resume_text:
        raise HTTPException(status_code=400, detail="No resume text available")

    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Prompt to extract skills
    prompt = f"""
    Extract a list of technical skills from this resume text.
    Only return a JSON array of strings, nothing else.
    Resume text:
    {candidate.resume_text[:2000]}
    """

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        skills_text = resp["choices"][0]["message"]["content"]

        try:
            skills = json.loads(skills_text)
        except:
            # fallback: wrap in array
            skills = [skills_text]

        candidate.skills = json.dumps(skills)
        db.commit()
        db.refresh(candidate)

        return {"candidate_id": candidate.id, "skills": skills}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
