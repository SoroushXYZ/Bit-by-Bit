# Use Python base image for CPU-only deployment
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-cpu.txt .
RUN pip install --no-cache-dir -r requirements-cpu.txt

# Copy pipeline code
COPY . .

# Create data directories
RUN mkdir -p data/raw data/processed data/output logs

# Expose Ollama port
EXPOSE 11434

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Start Ollama in background\n\
ollama serve &\n\
\n\
# Wait for Ollama to start\n\
sleep 5\n\
\n\
# Pull the required model\n\
echo "Pulling llama3.2:3b model..."\n\
ollama pull llama3.2:3b\n\
\n\
# Wait for model to be ready\n\
sleep 10\n\
\n\
# Run the pipeline\n\
echo "Starting pipeline..."\n\
python run_pipeline.py "$@"' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
