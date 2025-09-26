# Bit-by-Bit AI Newsletter - Docker Setup

This guide will help you set up and run the Bit-by-Bit AI Newsletter pipeline using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 8GB RAM available for Docker
- At least 10GB free disk space

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd Bit-by-Bit
   ```

2. **Run the setup script:**
   ```bash
   ./docker-setup.sh
   ```

   This script will:
   - Create necessary directories
   - Build the Docker image
   - Start the container with Ollama
   - Download the required AI models
   - Set up the complete environment

3. **Run the pipeline:**
   ```bash
   docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py
   ```

## Manual Setup

If you prefer to set up manually:

1. **Create directories:**
   ```bash
   mkdir -p pipeline/data/{raw,processed,output} pipeline/logs
   ```

2. **Create environment file:**
   ```bash
   cp env.example .env
   # Edit .env and add your Guardian API key if needed
   ```

3. **Build and start:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Wait for Ollama to start and pull models:**
   ```bash
   docker-compose exec bit-by-bit-pipeline ollama pull llama3.2:3b
   ```

## Usage Commands

### Running the Pipeline

**Full pipeline:**
```bash
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py
```

**Individual steps:**
```bash
# RSS Gathering
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering

# Content Filtering
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step content_filtering

# Ad Detection
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step ad_detection

# LLM Quality Scoring
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step llm_quality_scoring

# Deduplication
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step deduplication
```

**With verbose logging:**
```bash
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --verbose
```

### Testing

**Test individual components:**
```bash
# Test RSS gathering
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_rss_gathering.py

# Test content filtering
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_content_filtering.py

# Test ad detection
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_ad_detection.py

# Test LLM quality scoring
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_llm_quality_scoring.py
```

### Container Management

**Access the container shell:**
```bash
docker-compose exec bit-by-bit-pipeline bash
```

**View logs:**
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f bit-by-bit-pipeline
```

**Stop the container:**
```bash
docker-compose down
```

**Restart the container:**
```bash
docker-compose restart
```

**Rebuild and restart:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Data Persistence

The following directories are mounted as volumes to persist data:

- `./pipeline/data` → `/app/pipeline/data` (raw, processed, and output data)
- `./pipeline/logs` → `/app/pipeline/logs` (pipeline logs)
- `./pipeline/config` → `/app/pipeline/config` (configuration files)

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Guardian API (optional - only needed if using Guardian API)
GUARDIAN_API_KEY=your_guardian_api_key_here

# Ollama Configuration
OLLAMA_HOST=0.0.0.0:11434
```

### Pipeline Configuration

Edit configuration files in `pipeline/config/`:

- `pipeline_config.json` - Main pipeline settings
- `rss_feeds.json` - RSS feed list and settings
- `rss_gathering_config.json` - RSS gathering parameters
- `content_filtering_config.json` - Content filtering rules
- `ad_detection_config.json` - Ad detection model settings
- `llm_quality_scoring_config.json` - LLM quality scoring parameters
- `deduplication_config.json` - Deduplication settings

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check Docker logs
docker-compose logs bit-by-bit-pipeline

# Check if ports are available
netstat -tulpn | grep 11434
```

**Ollama not responding:**
```bash
# Check if Ollama is running inside container
docker-compose exec bit-by-bit-pipeline curl http://localhost:11434/api/tags

# Restart Ollama service
docker-compose exec bit-by-bit-pipeline pkill ollama
docker-compose exec bit-by-bit-pipeline ollama serve &
```

**Out of memory errors:**
- Increase Docker memory limit to at least 8GB
- Reduce batch sizes in configuration files
- Use smaller models (e.g., llama3.2:1b instead of llama3.2:3b)

**Model download fails:**
```bash
# Manually pull the model
docker-compose exec bit-by-bit-pipeline ollama pull llama3.2:3b

# Check available models
docker-compose exec bit-by-bit-pipeline ollama list
```

### Performance Optimization

**For faster startup:**
- Use smaller models (llama3.2:1b)
- Reduce RSS feed count in configuration
- Lower quality thresholds

**For better performance:**
- Increase Docker memory allocation
- Use SSD storage for data volumes
- Enable Docker BuildKit

## Monitoring

**Check container health:**
```bash
docker-compose ps
```

**Monitor resource usage:**
```bash
docker stats bit-by-bit-pipeline
```

**View pipeline logs:**
```bash
# Real-time logs
tail -f pipeline/logs/pipeline.log

# Or via Docker
docker-compose exec bit-by-bit-pipeline tail -f pipeline/logs/pipeline.log
```

## Development

**For development with live code changes:**
```bash
# Mount the source code as a volume
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  bit-by-bit-pipeline:
    volumes:
      - .:/app
      - /app/venv  # Exclude virtual environment
```

## Production Deployment

For production deployment:

1. **Use specific image tags**
2. **Set resource limits**
3. **Use external volumes for data**
4. **Configure proper logging**
5. **Set up monitoring and alerting**

Example production docker-compose:
```yaml
version: '3.8'
services:
  bit-by-bit-pipeline:
    image: bit-by-bit-newsletter:latest
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
    volumes:
      - /var/lib/bit-by-bit/data:/app/pipeline/data
      - /var/lib/bit-by-bit/logs:/app/pipeline/logs
```

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify configuration files
3. Ensure sufficient system resources
4. Check network connectivity for RSS feeds
5. Verify API keys if using external services

