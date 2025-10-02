# Use NVIDIA CUDA 12.2 base image for GPU support
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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