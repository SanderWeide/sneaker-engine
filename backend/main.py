import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db
from routes import auth_router, users_router, sneakers_router, propositions_router

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sneaker Engine API", version="1.0.0")

# Configure CORS for Angular frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
origins = [
    frontend_url,
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://127.0.0.1",
    "https://dev.sneaker-engine.com",
    "https://www.sneaker-engine.com",
    "https://sneaker-engine.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(sneakers_router)
app.include_router(propositions_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Sneaker Engine API"}


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query to verify DB connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
