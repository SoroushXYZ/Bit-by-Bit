#!/bin/bash

# Bit-by-Bit AI Newsletter Pipeline - Docker Setup Script

set -e

echo "🚀 Bit-by-Bit AI Newsletter Pipeline - Docker Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p pipeline/data/raw
mkdir -p pipeline/data/processed
mkdir -p pipeline/data/output
mkdir -p pipeline/logs

print_status "Directories created"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file and add your Guardian API key if needed"
    print_status ".env file created"
else
    print_status ".env file already exists"
fi

# Build the Docker image
print_info "Building Docker image..."
docker-compose build

print_status "Docker image built successfully"

# Start the container
print_info "Starting container..."
docker-compose up -d

print_status "Container started"

# Wait for Ollama to be ready
print_info "Waiting for Ollama to start and download models..."
print_warning "This may take several minutes on first run..."

# Check if Ollama is responding
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_status "Ollama is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 10
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Ollama failed to start within expected time"
    print_info "Check container logs: docker-compose logs"
    exit 1
fi

# Pull the required model
print_info "Ensuring llama3.2:3b model is available..."
docker-compose exec bit-by-bit-pipeline ollama pull llama3.2:3b

print_status "Setup complete!"

echo ""
echo "🎉 Bit-by-Bit AI Newsletter Pipeline is ready!"
echo "=============================================="
echo ""
echo "📋 Available commands:"
echo "  • Run full pipeline:     docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py"
echo "  • Run specific step:     docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering"
echo "  • Access container:      docker-compose exec bit-by-bit-pipeline bash"
echo "  • View logs:             docker-compose logs -f"
echo "  • Stop container:        docker-compose down"
echo "  • Restart container:     docker-compose restart"
echo ""
echo "📊 Test the pipeline:"
echo "  docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_rss_gathering.py"
echo ""
echo "🔧 Ollama is available at: http://localhost:11434"
echo ""

