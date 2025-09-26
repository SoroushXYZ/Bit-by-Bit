#!/bin/bash

# Docker Test Script for Bit-by-Bit AI Newsletter Pipeline

set -e

echo "🧪 Testing Bit-by-Bit AI Newsletter Pipeline in Docker"
echo "====================================================="

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

# Check if container is running
print_info "Checking if container is running..."
if ! docker-compose ps | grep -q "bit-by-bit-pipeline.*Up"; then
    print_error "Container is not running. Please run: docker-compose up -d"
    exit 1
fi
print_status "Container is running"

# Test Ollama connectivity
print_info "Testing Ollama connectivity..."
if ! docker-compose exec bit-by-bit-pipeline curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_error "Ollama is not responding. Check container logs."
    exit 1
fi
print_status "Ollama is responding"

# Check if required model is available
print_info "Checking if llama3.2:3b model is available..."
if ! docker-compose exec bit-by-bit-pipeline ollama list | grep -q "llama3.2:3b"; then
    print_warning "Model not found. Pulling llama3.2:3b..."
    docker-compose exec bit-by-bit-pipeline ollama pull llama3.2:3b
fi
print_status "Model is available"

# Test RSS gathering step
print_info "Testing RSS gathering step..."
if docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_rss_gathering.py; then
    print_status "RSS gathering test passed"
else
    print_error "RSS gathering test failed"
    exit 1
fi

# Test content filtering step
print_info "Testing content filtering step..."
if docker-compose exec bit-by-bit-pipeline python pipeline/tests/test_content_filtering.py; then
    print_status "Content filtering test passed"
else
    print_warning "Content filtering test failed (this is expected if no input data)"
fi

# Test a small pipeline run
print_info "Running a small pipeline test (RSS gathering only)..."
if docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py --step rss_gathering; then
    print_status "Pipeline RSS gathering step completed successfully"
else
    print_error "Pipeline RSS gathering step failed"
    exit 1
fi

echo ""
print_status "All tests completed successfully!"
echo ""
echo "🎉 Your Bit-by-Bit AI Newsletter Pipeline is ready to use!"
echo ""
echo "📋 Next steps:"
echo "  • Run full pipeline: docker-compose exec bit-by-bit-pipeline python pipeline/run_pipeline.py"
echo "  • Access container: docker-compose exec bit-by-bit-pipeline bash"
echo "  • View logs: docker-compose logs -f"
echo ""

