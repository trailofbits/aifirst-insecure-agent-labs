# Chatbot Agent Exploit Labs

A hands-on framework for testing prompt injection and system prompt extraction attacks with real-time guardrail protection, tracing, and agent tools. 

## Lab Notes

* Lab 1 - Become familiar with the chat bot. Try enabling and disabling guardrails. Create a Langsmith account, set an API key, and view all traces from the chat.
* Lab 2 - Force the system to call an internal page using (1) direct and (2) indirect prompt injection.
* Lab 3 - Extract the system prompt.
* Lab 4 - Access employee data for another user using (1) direct and (2) indirect prompt injection.

Note: Click the help menu for a list of all objectives and additional hints.

<img width="2532" height="1312" alt="CleanShot 2025-11-06 at 07 44 29" src="https://github.com/user-attachments/assets/8bdcb9bd-9b63-4dc7-8f23-007a52c91657" />


## Features

* Configurable input/output guardrails and regex validation that match real world deployments.
* Tracing (LangSmith) is configured for all inference. Guardrail violations are tracked.
* Each agent has access tools that pull in context from outside sources.
* Clear UI notification when you have completed a lab.

## Quick Start

### Prerequisites

1. **Docker or Podman** - Both supported! The quickstart script auto-detects which you have.
   - Docker: https://docs.docker.com/get-docker/
   - Podman: https://podman.io/getting-started/installation (also install `podman-compose`)

2. **Ollama** running locally with the llama3 and llama3-groq-tool-use models:
   ```bash
   # Install from https://ollama.ai

   ollama serve
   ollama pull llama3-groq-tool-use:8b
   ollama pull llama3
   ```

### Installation

```bash
# Run the quickstart script (handles everything automatically)
./quickstart.sh
```

The script will auto-detect Docker/Podman, configure Ollama connectivity, build containers, and start all services.

## Testing Indirect Prompt Injections

### Basic Workflow

All labs are available at http://localhost:3000

## Guardrails

The framework uses **NVIDIA NeMo Guardrails** and custom regex Guardrails. 

**Configuration:**
- Main config: `backend/config/nemo/config.yml`
- Lightweight config: `backend/config/nemo/config.light.yml` (not used right now)
- See `backend/config/nemo/README.md` for tuning options

## Useful Commands

```bash
# View logs
docker compose logs -f
# Or: podman compose logs -f

# View specific service
docker compose logs -f backend

# Restart a service
docker compose restart backend

# Stop everything
docker compose down

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running on host
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Verify model is available
ollama list | grep llama3
```

### Backend Not Starting

```bash
# Check logs for errors
docker compose logs backend

# Rebuild backend container
docker compose build backend --no-cache
docker compose up -d backend
```

### Frontend Not Loading

```bash
# Verify backend is healthy
curl http://localhost:8000/health

# Check frontend logs
docker compose logs frontend
```

### Podman on Linux - Ollama Not Reachable

If using Podman on Linux and containers can't reach Ollama:

```bash
# The quickstart script handles this automatically, but if needed manually:
# Update OLLAMA_HOST in .env files from:
#   http://host.docker.internal:11434
# To:
#   http://host.containers.internal:11434
```
## Extending the Labs

### Customize Guardrail Detection

**Option 1: Tune NeMo Guardrails (Recommended)**

Edit `backend/config/nemo/config.yml` to adjust detection thresholds or add custom policies:

```yaml
rails:
  config:
    jailbreak_detection:
      length_per_perplexity_threshold: 75.0  # Lower = more sensitive

prompts:
  - task: self_check_input
    content: |
      Add your custom security policies here...
```

**Option 2: Add Custom Regex Patterns (Legacy)**

If using `USE_NEMO_GUARDRAILS=false`, edit `backend/guardrails/patterns.py`:

```python
INJECTION_PATTERNS = [
    r'your_custom_pattern',
    r'another_pattern',
]
```

**Apply Changes:**

```bash
docker compose restart backend
# Or: podman compose restart backend
```

See `backend/config/nemo/README.md` for detailed tuning guide.

