from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from routes import users_router, sneakers_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sneaker Engine API", version="1.0.0")

# Configure CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(sneakers_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Sneaker Engine API"}


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query to verify DB connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
