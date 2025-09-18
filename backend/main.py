# backend/main.py
import os
import io
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()  # loads .env if present
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

app = FastAPI(title="Hackathon FastAPI")

# Allow frontend running on localhost:3000 to call this API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping():
    return {"status": "ok"}

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: AskRequest):
    """Simple wrapper around an OpenAI chat call. Replace model as needed."""
    if not openai.api_key:
        return {"error": "OPENAI_API_KEY not set on server."}
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request.question}],
            max_tokens=500,
            temperature=0.2
        )
        # getting answer from response (works with common library versions)
        answer = None
        if resp.choices and len(resp.choices) > 0:
            # new style: .choices[0].message.content
            choice = resp.choices[0]
            if hasattr(choice, "message") and choice.message:
                answer = choice.message.get("content")
            else:
                # fallback to text
                answer = choice.get("text", "")
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Accepts a CSV upload, returns summary stats and a base64 PNG chart.
    (Keep demo datasets small.)
    """
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        return {"error": "Failed to read CSV: " + str(e)}
    # simple stats
    stats = df.describe().to_dict()

    # make a simple plot (first two numeric cols if available)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    chart_b64 = None
    if len(numeric_cols) >= 1:
        # create a histogram for the first numeric column
        col0 = numeric_cols[0]
        plt.figure(figsize=(6, 4))
        plt.hist(df[col0].dropna(), bins=20)
        plt.title(f"Histogram of {col0}")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        chart_b64 = base64.b64encode(buf.read()).decode("utf-8")
        chart_b64 = f"data:image/png;base64,{chart_b64}"

    return {"stats": stats, "chart": chart_b64}
