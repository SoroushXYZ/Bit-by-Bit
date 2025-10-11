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

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /data/runs` - List all pipeline runs
- `POST /data/update` - Update data from S3

## Configuration

See `.env.example` for available configuration options.

