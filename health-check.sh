#!/bin/bash

# Health check script for Docker container

# Check if Ollama is responding
if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    exit 0
else
    exit 1
fi

