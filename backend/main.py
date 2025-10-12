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

@app.get("/data/runs")
async def get_runs(request: Request, _: bool = Depends(check_ip_whitelist)):
    """Get all available pipeline runs."""
    try:
        s3 = get_s3_service()
        runs = s3.list_runs()
        return {
            "status": "success",
            "total_runs": len(runs),
            "runs": runs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch runs: {str(e)}")

@app.get("/data/runs/{run_id}")
async def get_run_data(run_id: str, request: Request, summary: bool = Query(False, description="Return summary only"), _: bool = Depends(check_ip_whitelist)):
    """Get data for a specific pipeline run."""
    try:
        s3 = get_s3_service()
        if summary:
            data = s3.get_run_summary(run_id)
        else:
            data = s3.get_run_data(run_id)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        
        return {
            "status": "success",
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch run data: {str(e)}")

@app.get("/data/runs/latest")
async def get_latest_run(request: Request, _: bool = Depends(check_ip_whitelist)):
    """Get the most recent pipeline run."""
    try:
        s3 = get_s3_service()
        data = s3.get_latest_run()
        if not data:
            raise HTTPException(status_code=404, detail="No runs found")
        
        return {
            "status": "success",
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest run: {str(e)}")

@app.post("/data/update")
async def update_data(request: Request, _: bool = Depends(check_ip_whitelist)):
    """Update/sync data from S3 bucket."""
    try:
        s3 = get_s3_service()
        sync_result = s3.sync_data()
        return {
            "status": "success",
            "message": "Data sync completed",
            "result": sync_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync data: {str(e)}")

@app.get("/data/stats")
async def get_stats(request: Request, _: bool = Depends(check_ip_whitelist)):
    """Get overall statistics about pipeline runs."""
    try:
        s3 = get_s3_service()
        runs = s3.list_runs()
        
        # Filter out None values
        valid_runs = [run for run in runs if run is not None]
        
        # Calculate basic stats
        total_runs = len(valid_runs)
        total_files = sum(run.get('total_files', 0) for run in valid_runs)
        
        # Group by environment
        env_counts = {}
        for run in valid_runs:
            env = run.get('environment', 'unknown')
            env_counts[env] = env_counts.get(env, 0) + 1
        
        return {
            "status": "success",
            "stats": {
                "total_runs": total_runs,
                "total_files": total_files,
                "environment_counts": env_counts,
                "runs_with_metadata": sum(1 for run in valid_runs if run.get('has_metadata', False))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Local sync endpoints
@app.post("/sync/local")
async def sync_local_data(request: Request, _: bool = Depends(check_ip_whitelist)):
    """Sync all data from S3 to local storage."""
    try:
        sync_service = get_local_sync_service()
        result = sync_service.sync_all_runs()
        return {
            "status": "success",
            "message": "Local sync completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync local data: {str(e)}")

@app.get("/local/runs")
async def get_local_runs():
    """Get all locally stored runs."""
    try:
        sync_service = get_local_sync_service()
        local_runs = sync_service._get_local_runs()
        return {
            "status": "success",
            "total_runs": len(local_runs),
            "runs": local_runs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get local runs: {str(e)}")

@app.get("/local/runs/{run_id}")
async def get_local_run_data(run_id: str, summary: bool = Query(False, description="Return summary only")):
    """Get data for a locally stored run."""
    try:
        sync_service = get_local_sync_service()
        data = sync_service.get_local_run_data(run_id)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Local run {run_id} not found")
        
        if summary:
            # Return summary
            return {
                "status": "success",
                "data": {
                    "run_id": data["run_id"],
                    "total_files": len(data["all_files"]),
                    "raw_files": data["raw_data"]["total_files"],
                    "processed_files": data["processed_data"]["total_files"],
                    "output_files": data["output_data"]["total_files"],
                    "log_files": data["logs"]["total_files"],
                    "local_path": data["local_path"],
                    "metadata": data["metadata"]
                }
            }
        else:
            # Return full data
            return {
                "status": "success",
                "data": data
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get local run data: {str(e)}")

@app.get("/local/stats")
async def get_local_stats():
    """Get statistics about locally stored data."""
    try:
        sync_service = get_local_sync_service()
        local_runs = sync_service._get_local_runs()
        
        total_files = 0
        total_size = 0
        
        for run in local_runs:
            run_path = run['path']
            for root, dirs, files in os.walk(run_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        total_files += 1
                        total_size += os.path.getsize(file_path)
        
        return {
            "status": "success",
            "stats": {
                "total_runs": len(local_runs),
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "local_data_dir": sync_service.local_data_dir
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get local stats: {str(e)}")

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
