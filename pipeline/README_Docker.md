# Bit-by-Bit Pipeline Docker Setup

## Quick Start

1. **Build and run the pipeline:**
   ```bash
   docker-compose up --build
   ```

2. **Run specific pipeline steps:**
   ```bash
   docker-compose run --rm pipeline --step data_collection
   docker-compose run --rm pipeline --step processing
   ```

3. **Run with verbose logging:**
   ```bash
   docker-compose run --rm pipeline --step all --verbose
   ```

## What's Included

- **Python 3.12** with all pipeline dependencies
- **Ollama** with llama3.2:3b model pre-loaded
- **NVIDIA GPU support** for transformers and Ollama
- **Volume mounts** for data persistence
- **Automatic model download** on first run

## Data Persistence

- `./data/` - All pipeline data (raw, processed, output)
- `./config/` - Configuration files
- `./logs/` - Pipeline logs

## GPU Requirements

- NVIDIA GPU with CUDA support
- Docker with NVIDIA Container Toolkit
- nvidia-docker2 installed

## Troubleshooting

- **GPU not detected**: Ensure nvidia-docker2 is installed
- **Model download fails**: Check internet connection and Ollama logs
- **Permission issues**: Ensure data directories are writable
