from fastapi import FastAPI
from sqlalchemy.orm import Session

app = FastAPI(title="Fixture API")

@app.get("/health")
def health():
    return {"status": "ok"}
