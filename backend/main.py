"""
Bit-by-Bit Backend API
FastAPI application for managing pipeline data from S3.
"""

from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
from dotenv import load_dotenv
from services.s3_service import S3Service
from services.local_sync import LocalSyncService

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

# Initialize S3 service (lazy initialization)
s3_service = None
local_sync_service = None

# IP Whitelist configuration
def get_allowed_ips():
    """Get list of allowed IP addresses from environment."""
    allowed_ips_str = os.getenv("ALLOWED_IPS", "0.0.0.0")
    if not allowed_ips_str or allowed_ips_str.strip() == "":
        return ["0.0.0.0"]  # Default to allow all
    
    # Split by comma and clean up
    allowed_ips = [ip.strip() for ip in allowed_ips_str.split(",") if ip.strip()]
    
    # If empty after cleaning, default to allow all
    if not allowed_ips:
        return ["0.0.0.0"]
    
    return allowed_ips

def check_ip_whitelist(request: Request):
    """Check if client IP is in whitelist."""
    client_ip = request.client.host
    allowed_ips = get_allowed_ips()
    
    # Allow all if 0.0.0.0 is in the list
    if "0.0.0.0" in allowed_ips:
        return True
    
    # Check if client IP is in allowed list
    if client_ip not in allowed_ips:
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied. IP {client_ip} not in whitelist. Allowed IPs: {', '.join(allowed_ips)}"
        )
    
    return True

def get_s3_service():
    """Get S3 service instance (lazy initialization)."""
    global s3_service
    if s3_service is None:
        s3_service = S3Service()
    return s3_service

def get_local_sync_service():
    """Get local sync service instance (lazy initialization)."""
    global local_sync_service
    if local_sync_service is None:
        s3 = get_s3_service()
        local_sync_service = LocalSyncService(s3)
    return local_sync_service

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Bit-by-Bit Backend API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test S3 connection
        s3 = get_s3_service()
        runs = s3.list_runs()
        return {
            "status": "healthy",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "s3_connected": True,
            "total_runs": len(runs)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "s3_connected": False,
            "error": str(e)
        }

@app.post("/sync")
async def sync_data(request: Request, _: bool = Depends(check_ip_whitelist)):
    """Sync all data from S3 to local storage with efficient incremental updates."""
    try:
        sync_service = get_local_sync_service()
        result = sync_service.sync_all_runs()
        return {
            "status": "success",
            "message": "Data sync completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync data: {str(e)}")

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
