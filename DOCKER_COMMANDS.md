# 🐳 Docker Commands Quick Reference

## 🚀 Setup & Initialization

```bash
# Automated setup (recommended)
./docker-setup.sh

# Manual setup
docker-compose build
docker-compose up -d

# Verify setup
./verify-setup.sh
```

## 📊 Running the Pipeline

```bash
# Complete pipeline
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py

# Individual steps
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step content_filtering
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step ad_detection
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step llm_quality_scoring
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step deduplication

# With verbose logging
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --verbose
```

## 🧪 Testing

```bash
# Quick test suite
./test-docker.sh

# Individual component tests
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_rss_gathering.py
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_content_filtering.py
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_ad_detection.py
docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_llm_quality_scoring.py
```

## 🔧 Container Management

```bash
# Start container
docker-compose up -d

# Stop container
docker-compose down

# Restart container
docker-compose restart

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
```

## 📝 Access & Debugging

```bash
# Access container shell
docker-compose exec bit-by-bit-pipeline bash

# View logs
docker-compose logs -f bit-by-bit-pipeline

# View specific logs
docker-compose logs -f bit-by-bit-pipeline | grep "ERROR"

# Monitor resources
docker stats bit-by-bit-pipeline
```

## 🤖 Ollama Management

```bash
# Check Ollama status
docker-compose exec bit-by-bit-pipeline curl http://localhost:11434/api/tags

# List available models
docker-compose exec bit-by-bit-pipeline ollama list

# Pull additional models
docker-compose exec bit-by-bit-pipeline ollama pull llama3.2:1b

# Restart Ollama service
docker-compose exec bit-by-bit-pipeline pkill ollama
docker-compose exec bit-by-bit-pipeline ollama serve &
```

## 📁 Data Management

```bash
# View collected data
ls -la pipeline/data/

# View raw RSS data
ls -la pipeline/data/raw/

# View processed data
ls -la pipeline/data/processed/

# View final output
ls -la pipeline/data/output/

# View logs
tail -f pipeline/logs/pipeline.log
```

## 🔍 Troubleshooting

```bash
# Check container health
docker-compose ps

# View detailed logs
docker-compose logs bit-by-bit-pipeline

# Check if Ollama is responding
curl http://localhost:11434/api/tags

# Check disk space
docker system df

# Clean up unused resources
docker system prune
```

## 📊 Monitoring

```bash
# Real-time resource usage
docker stats bit-by-bit-pipeline

# Container health check
docker inspect bit-by-bit-pipeline | grep -A 10 "Health"

# Log monitoring
docker-compose logs -f bit-by-bit-pipeline | grep -E "(ERROR|WARNING|INFO)"
```

## 🛠️ Development

```bash
# Rebuild with no cache
docker-compose build --no-cache

# Run with live code mounting (for development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Execute Python commands in container
docker-compose exec bit-by-bit-pipeline python -c "print('Hello from container!')"

# Install additional packages
docker-compose exec bit-by-bit-pipeline pip install package-name
```

## 📋 Common Workflows

### First-time setup:
```bash
./docker-setup.sh
./verify-setup.sh
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering
```

### Daily pipeline run:
```bash
docker-compose up -d
docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py
docker-compose logs -f bit-by-bit-pipeline
```

### Debugging issues:
```bash
docker-compose logs bit-by-bit-pipeline
docker-compose exec bit-by-bit-pipeline bash
# Inside container: python pipeline/run_pipeline.py --step rss_gathering --verbose
```

### Full reset:
```bash
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

