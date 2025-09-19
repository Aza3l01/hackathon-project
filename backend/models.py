# backend/models.py
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    skills = Column(Text)  # store JSON array as string

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    resume_text = Column(Text)
    skills = Column(Text)  # JSON array as string

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, index=True)
    job_id = Column(Integer, index=True)
    score = Column(Integer)
    matched_skills = Column(Text)
    missing_skills = Column(Text)
