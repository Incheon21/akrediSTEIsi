from fastapi import FastAPI
from app.db import engine, Base
from app.models import Role, User, ProgramStudi

app = FastAPI(title="STEI Akreditasi API", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}
