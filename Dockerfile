# Bit-by-Bit AI Newsletter Pipeline Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including GPU support
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p pipeline/data/raw pipeline/data/processed pipeline/data/output pipeline/logs

# Set permissions
RUN chmod +x pipeline/run_pipeline.py

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Bit-by-Bit AI Newsletter Pipeline"\n\
echo "📥 Starting Ollama server..."\n\
ollama serve &\n\
sleep 10\n\
echo "📚 Pulling required models..."\n\
ollama pull llama3.2:3b\n\
echo "✅ Setup complete! Ready to run pipeline."\n\
echo "💡 Use: docker exec -it <container> python pipeline/run_pipeline.py"\n\
echo "💡 Or: docker exec -it <container> bash"\n\
tail -f /dev/null' > /app/start.sh && chmod +x /app/start.sh

# Expose Ollama port
EXPOSE 11434

# Set the startup script as entrypoint
ENTRYPOINT ["/app/start.sh"]
