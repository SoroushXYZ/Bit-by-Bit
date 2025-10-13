# Bit-by-Bit Backend API

FastAPI backend service for managing newsletter pipeline data from S3.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

3. Run the server:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with basic info
- `GET /health` - Health check with S3 connection status

### Data Management
- `GET /data/runs` - List all pipeline runs
- `GET /data/runs/{run_id}` - Get specific run data (full or summary)
- `GET /data/runs/latest` - Get the most recent run
- `GET /data/stats` - Get overall statistics
- `POST /data/update` - Sync/update data from S3

### Query Parameters
- `?summary=true` - Return summary only for run data

## Testing

Run the test script:
```bash
python test_api.py
```

## Configuration

See `.env.example` for available configuration options.

## Features

- ✅ S3 data fetching and management
- ✅ Environment-aware bucket selection
- ✅ Run metadata and file content retrieval
- ✅ Statistics and health monitoring
- ✅ Public endpoints (no authentication)
- ✅ CORS enabled for frontend integration

