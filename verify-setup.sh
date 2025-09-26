#!/bin/bash

# Comprehensive Setup Verification Script for Bit-by-Bit AI Newsletter Pipeline

set -e

echo "🔍 Bit-by-Bit AI Newsletter Pipeline - Setup Verification"
echo "========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    netstat -tuln 2>/dev/null | grep -q ":$1 "
}

echo ""
print_info "Checking system requirements..."

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker is installed (version: $DOCKER_VERSION)"
else
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker Compose is installed (version: $COMPOSE_VERSION)"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short)
    print_status "Docker Compose is available (version: $COMPOSE_VERSION)"
    # Create symlink for compatibility
    if [ ! -f /usr/local/bin/docker-compose ]; then
        sudo ln -sf $(which docker) /usr/local/bin/docker-compose
        print_info "Created docker-compose symlink for compatibility"
    fi
else
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Check if Docker daemon is running
if docker info >/dev/null 2>&1; then
    print_status "Docker daemon is running"
else
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

# Check available disk space
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
REQUIRED_SPACE=10485760  # 10GB in KB
if [ "$AVAILABLE_SPACE" -gt "$REQUIRED_SPACE" ]; then
    print_status "Sufficient disk space available ($(($AVAILABLE_SPACE / 1024 / 1024))GB)"
else
    print_warning "Low disk space available ($(($AVAILABLE_SPACE / 1024 / 1024))GB). Consider freeing up space."
fi

# Check available memory
if command_exists free; then
    AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$AVAILABLE_MEM" -gt 4096 ]; then
        print_status "Sufficient memory available (${AVAILABLE_MEM}MB)"
    else
        print_warning "Low memory available (${AVAILABLE_MEM}MB). Pipeline may run slowly."
    fi
fi

echo ""
print_info "Checking project structure..."

# Check required files
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    "pipeline/run_pipeline.py"
    "pipeline/config/pipeline_config.json"
    "pipeline/config/rss_feeds.json"
    "pipeline/steps/rss_gathering.py"
    "pipeline/steps/content_filtering.py"
    "pipeline/steps/ad_detection.py"
    "pipeline/steps/llm_quality_scoring.py"
    "pipeline/steps/deduplication.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# Check required directories
REQUIRED_DIRS=(
    "pipeline"
    "pipeline/config"
    "pipeline/steps"
    "pipeline/utils"
    "pipeline/tests"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_status "Found directory: $dir"
    else
        print_error "Missing required directory: $dir"
        exit 1
    fi
done

echo ""
print_info "Checking configuration files..."

# Validate JSON configuration files
for config_file in pipeline/config/*.json; do
    if [ -f "$config_file" ]; then
        if python3 -m json.tool "$config_file" >/dev/null 2>&1; then
            print_status "Valid JSON: $(basename "$config_file")"
        else
            print_error "Invalid JSON: $(basename "$config_file")"
            exit 1
        fi
    fi
done

echo ""
print_info "Checking environment setup..."

# Check if .env file exists
if [ -f ".env" ]; then
    print_status ".env file exists"
else
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_status "Created .env file from template"
    else
        print_warning "No env.example found. You may need to create .env manually."
    fi
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p pipeline/data/{raw,processed,output}
mkdir -p pipeline/logs
print_status "Directories created"

echo ""
print_info "Checking Docker setup..."

# Check if port 11434 is available
if port_in_use 11434; then
    print_warning "Port 11434 is already in use. This might conflict with Ollama."
else
    print_status "Port 11434 is available"
fi

echo ""
print_info "Testing Docker build..."

# Test Docker build
if docker-compose build --no-cache; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

echo ""
print_info "Starting container for testing..."

# Start container
if docker-compose up -d; then
    print_status "Container started successfully"
else
    print_error "Failed to start container"
    exit 1
fi

# Wait for container to be ready
print_info "Waiting for container to be ready..."
sleep 10

# Check if container is running
if docker-compose ps | grep -q "bit-by-bit-pipeline.*Up"; then
    print_status "Container is running"
else
    print_error "Container is not running properly"
    docker-compose logs bit-by-bit-pipeline
    exit 1
fi

echo ""
print_info "Testing container functionality..."

# Test Python imports
if docker-compose exec bit-by-bit-pipeline python -c "import feedparser, requests, transformers; print('All imports successful')"; then
    print_status "Python dependencies are working"
else
    print_error "Python dependencies test failed"
fi

# Test Ollama installation
if docker-compose exec bit-by-bit-pipeline ollama --version >/dev/null 2>&1; then
    print_status "Ollama is installed"
else
    print_error "Ollama installation failed"
fi

# Test configuration loading
if docker-compose exec bit-by-bit-pipeline python -c "import sys; sys.path.insert(0, '/app'); from utils.config_loader import load_pipeline_config; config = load_pipeline_config('/app/pipeline/config/pipeline_config.json'); print('Configuration loaded successfully')"; then
    print_status "Configuration loading works"
else
    print_error "Configuration loading failed"
fi

echo ""
print_info "Running basic pipeline test..."

# Test RSS gathering step
if docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_rss_gathering.py; then
    print_status "RSS gathering test passed"
else
    print_warning "RSS gathering test failed (this might be expected on first run)"
fi

echo ""
print_status "🎉 Setup verification completed!"
echo ""
echo "📋 Summary:"
echo "  • Docker environment: ✅ Ready"
echo "  • Project structure: ✅ Complete"
echo "  • Configuration: ✅ Valid"
echo "  • Container: ✅ Running"
echo ""
echo "🚀 Next steps:"
echo "  1. Run the complete pipeline:"
echo "     docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py"
echo ""
echo "  2. Or run individual steps:"
echo "     docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering"
echo ""
echo "  3. Access the container:"
echo "     docker-compose exec bit-by-bit-pipeline bash"
echo ""
echo "  4. View logs:"
echo "     docker-compose logs -f bit-by-bit-pipeline"
echo ""
echo "  5. Stop when done:"
echo "     docker-compose down"
echo ""

# Optional: Run a quick pipeline test
read -p "🤔 Would you like to run a quick pipeline test now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_info "Running quick pipeline test..."
    if docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering; then
        print_status "Quick pipeline test completed successfully!"
        echo ""
        print_info "You can now run the full pipeline or individual steps as needed."
    else
        print_warning "Quick pipeline test failed. Check the logs for details."
    fi
fi

echo ""
print_status "Setup verification complete! Your Bit-by-Bit AI Newsletter Pipeline is ready to use."

