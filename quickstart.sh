#!/bin/bash

# Chatbot Framework Quick Start Script
# Supports both Docker and Podman

set -e

echo "Chatbot Framework - Quick Start"
echo "===================================="
echo ""

# Detect container runtime
CONTAINER_CMD=""
COMPOSE_CMD=""

if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
    CONTAINER_CMD="docker"
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif docker-compose --version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    fi
    echo "✅ Detected: Docker"
elif command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    # Check if 'podman compose' works (built-in or external provider)
    if podman compose version >/dev/null 2>&1; then
        COMPOSE_CMD="podman compose"
    # Fallback to podman-compose if available
    elif command -v podman-compose &> /dev/null; then
        COMPOSE_CMD="podman-compose"
    fi
    echo "✅ Detected: Podman"
else
    echo "❌ Error: Neither Docker nor Podman found. Please install one of them:"
    echo "   Docker: https://docs.docker.com/get-docker/"
    echo "   Podman: https://podman.io/getting-started/installation"
    exit 1
fi

if [ -z "$COMPOSE_CMD" ]; then
    echo "❌ Error: Compose command not found."
    if [ "$CONTAINER_CMD" = "docker" ]; then
        echo "   For Docker, install Docker Compose plugin or docker-compose"
        echo "   See: https://docs.docker.com/compose/install/"
    else
        echo "   For Podman, install podman-compose:"
        echo "   "
        echo "   # Using pip"
        echo "   pip3 install podman-compose"
        echo "   "
        echo "   # Or using pipx (recommended)"
        echo "   pipx install podman-compose"
        echo "   "
        echo "   # On Fedora/RHEL"
        echo "   sudo dnf install podman-compose"
        echo "   "
        echo "   See: https://github.com/containers/podman-compose"
    fi
    exit 1
fi

echo "   Using: $COMPOSE_CMD"
echo ""

# Determine Ollama host based on container runtime
if [ "$CONTAINER_CMD" = "podman" ]; then
    # Check if running on Linux (needs host.containers.internal)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OLLAMA_DEFAULT_HOST="http://host.containers.internal:11434"
    else
        # Mac/Windows with Podman
        OLLAMA_DEFAULT_HOST="http://host.docker.internal:11434"
    fi
else
    # Docker uses host.docker.internal on all platforms
    OLLAMA_DEFAULT_HOST="http://host.docker.internal:11434"
fi

# Check if Ollama is running on host
echo "Checking Ollama on host machine..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"

    # Check if llama3 model is available
    if curl -s http://localhost:11434/api/tags | grep -q "llama3"; then
        echo "✅ llama3 model is available"
    else
        echo "⚠️  Warning: llama3 model not found"
        echo "   Pull it with: ollama pull llama3"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  Warning: Ollama doesn't appear to be running on localhost:11434"
    echo "   You may need to start Ollama with: ollama serve"
    echo "   And pull the model with: ollama pull llama3"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create .env files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    # Update OLLAMA_HOST based on detected runtime
    if [[ "$OSTYPE" == "linux-gnu"* ]] && [ "$CONTAINER_CMD" = "podman" ]; then
        sed -i 's|OLLAMA_HOST=.*|OLLAMA_HOST=http://host.containers.internal:11434|' backend/.env 2>/dev/null || \
        sed -i '' 's|OLLAMA_HOST=.*|OLLAMA_HOST=http://host.containers.internal:11434|' backend/.env
    fi
    echo "   Please edit backend/.env to add your API keys if needed"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend/.env from example..."
    cp frontend/.env.example frontend/.env
fi

echo ""
echo "🔨 Building containers with $COMPOSE_CMD..."
$COMPOSE_CMD build

echo ""
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check service health
echo ""
echo "🏥 Checking service health..."
if curl -s http://localhost:8181/health > /dev/null 2>&1; then
    echo "✅ Content Server: healthy"
else
    echo "⚠️  Content Server: not responding"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API: healthy"
else
    echo "⚠️  Backend API: not responding (may still be starting...)"
fi

echo ""
echo "✅ Chatbot Framework is running!"
echo ""
echo "📍 Access the application:"
echo "   Frontend:       http://localhost:3000"
echo "   Backend API:    http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   Content Server: http://localhost:8181"
echo ""
echo "📋 Useful commands (using $COMPOSE_CMD):"
echo "   View logs:      $COMPOSE_CMD logs -f"
echo "   Stop services:  $COMPOSE_CMD down"
echo "   Restart:        $COMPOSE_CMD restart"
echo ""
echo ""
echo "💡 Container Runtime: $CONTAINER_CMD"
echo "   Ollama Host: $OLLAMA_DEFAULT_HOST"
echo ""
echo "Happy testing! 🎉"
