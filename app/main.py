
from __future__ import annotations

from pathlib import Path
from typing import Optional

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
VECT_PATH = APP_DIR / "vectorizer.pkl"
MODEL_PATH = APP_DIR / "model.pkl"

app = FastAPI(title="SMS Spam Classifier API", version="1.0")

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="SMS message text")

class PredictResponse(BaseModel):
    label: str
    score: Optional[float] = None

vectorizer = None
model = None

@app.on_event("startup")
def load_artifacts() -> None:
    global vectorizer, model
    if not VECT_PATH.exists() or not MODEL_PATH.exists():
        raise RuntimeError(
            "Model artifacts not found. Run training first:\n"
            "  python train/download_dataset.py\n"
            "  python train/train.py"
        )
    vectorizer = joblib.load(VECT_PATH)
    model = joblib.load(MODEL_PATH)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    global vectorizer, model
    if vectorizer is None or model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    X = vectorizer.transform([text])
    pred = model.predict(X)[0]

    score = None
    # Try to produce a probability-like score when available
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        score = float(proba.max())
    elif hasattr(model, "decision_function"):
        # margin score (not a probability); squash to (0,1) for nicer UX
        import math
        margin = float(model.decision_function(X)[0])
        score = 1.0 / (1.0 + math.exp(-margin))

    return PredictResponse(label=str(pred), score=score)
