# NeMo Guardrails Configuration

This directory contains configuration files for NVIDIA NeMo Guardrails integration.

## Files

- **config.yml** - Full NeMo Guardrails configuration with input and output rails
- **config.light.yml** - Lightweight configuration using only heuristic-based detection (faster)

## Configuration Overview

### config.yml (Full Configuration)

Uses both heuristic-based and LLM-based detection:

**Input Rails:**
- `self check input` - LLM evaluates user input against policy

**Output Rails:**
- `self check output` - LLM evaluates bot responses against policy

**Performance:** Slower but more sophisticated (includes 2 extra LLM calls per conversation turn)

### config.light.yml (Lightweight Configuration)

Uses only heuristic-based detection:

**Input Rails:** None (for performance)

**Output Rails:** None (for performance)

**Performance:** Faster, suitable for real-time demos

## Switching Configurations

Set environment variable in `backend/.env`:

```bash
# Use full configuration (default)
NEMO_LIGHT_CONFIG=false

# Use lightweight configuration
NEMO_LIGHT_CONFIG=true
```

## Custom Prompts

The `prompts` section in `config.yml` defines how the LLM judges input and output:

**self_check_input:** Checks if user input violates policy
- Looks for: instruction override, role manipulation, credential harvesting, etc.

**self_check_output:** Checks if bot response violates policy
- Looks for: leaked credentials, revealed system prompts, sensitive data exposure

## Customization

To add custom detection patterns:

1. Edit the `prompts` section in `config.yml`
2. Add your policy rules to the prompts
3. Adjust thresholds in the `config` section
4. Restart the backend container

## Disabling NeMo Guardrails

To fall back to the original regex-based guardrails:

```bash
# In backend/.env
USE_NEMO_GUARDRAILS=false
```

## Resources

- [NeMo Guardrails Documentation](https://docs.nvidia.com/nemo/guardrails/)
- [Configuration Guide](https://docs.nvidia.com/nemo/guardrails/latest/user-guides/configuration-guide.html)
- [Jailbreak Detection](https://docs.nvidia.com/nemo/guardrails/latest/user-guides/jailbreak-detection-heuristics/)
