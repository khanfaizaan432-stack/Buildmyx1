from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env", override=True)

# Import route modules
from api.routes import optimizer_router, squad_router

app = FastAPI(
    title="Build My XI API",
    description="Squad optimization and analysis API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React fallback
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(optimizer_router, prefix="/api")
app.include_router(squad_router, prefix="/api")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Build My XI API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # reload=True requires an import string (e.g. "main:app"), not the app object
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
