"""
Bit-by-Bit Backend API
FastAPI application for managing pipeline data from S3.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Bit-by-Bit Backend API",
    description="Backend service for managing newsletter pipeline data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bit-by-Bit Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/data/runs")
async def get_runs():
    """Get all available pipeline runs."""
    # TODO: Implement S3 data fetching
    return {
        "message": "Get runs endpoint - to be implemented",
        "runs": []
    }

@app.post("/data/update")
async def update_data():
    """Update data from S3 bucket."""
    # TODO: Implement data update logic
    return {
        "message": "Update data endpoint - to be implemented",
        "status": "pending"
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
