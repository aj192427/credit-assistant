"""
Credit Assistant API entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, credit, advisor

# Creates tables on startup if they don't exist yet. For production, prefer
# Alembic migrations instead of relying on this.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Credit Assistant API",
    description="AI-driven credit health platform for the Indian financial ecosystem.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(credit.router)
app.include_router(advisor.router)


@app.get("/health", tags=["meta"])
def health_check():
    return {"status": "ok"}
