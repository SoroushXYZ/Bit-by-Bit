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
from services.newsletter_service import NewsletterService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Bit-by-Bit Backend API",
    description="Backend service for managing newsletter pipeline data",
    version="1.0.0"
)

# Add CORS middleware
# Get allowed origins from environment, default to allow all in development
allowed_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "*")
if allowed_origins_env == "*":
    allowed_origins = ["*"]
else:
    # Split comma-separated origins
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization)
s3_service = None
local_sync_service = None
newsletter_service = None

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

def get_newsletter_service():
    """Get newsletter service instance (lazy initialization)."""
    global newsletter_service
    if newsletter_service is None:
        newsletter_service = NewsletterService()
    return newsletter_service

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

@app.get("/newsletter/dates")
async def get_newsletter_dates():
    """Get all available newsletter dates from local data folder."""
    try:
        newsletter_service = get_newsletter_service()
        dates = newsletter_service.get_available_dates()
        return {
            "status": "success",
            "total_dates": len(dates),
            "dates": dates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get newsletter dates: {str(e)}")

@app.get("/newsletter/grid")
async def get_newsletter_grid(date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. If not provided, returns latest")):
    """Get filled grid blueprint for newsletter."""
    try:
        newsletter_service = get_newsletter_service()
        
        if date:
            # Get latest run for specific date
            run_data = newsletter_service.get_latest_run_for_date(date)
            if not run_data:
                raise HTTPException(status_code=404, detail=f"No data found for date: {date}")
        else:
            # Get latest run overall
            run_data = newsletter_service.get_latest_run()
            if not run_data:
                raise HTTPException(status_code=404, detail="No newsletter data found")
        
        # Get the filled grid blueprint from output folder
        grid_data = newsletter_service.get_filled_grid_blueprint(run_data['run_id'])
        if not grid_data:
            raise HTTPException(status_code=404, detail="Filled grid blueprint not found")
        
        return {
            "status": "success",
            "run_id": run_data['run_id'],
            "date": run_data.get('date'),
            "grid_data": grid_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get newsletter grid: {str(e)}")

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
