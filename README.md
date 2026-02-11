# Moltworker Conversation

A Home Assistant custom component that connects to [Moltworker](https://github.com/cloudflare/moltworker) — OpenClaw running on Cloudflare Workers — as the AI backend for conversation and AI task platforms.

> **Based on [openclaw_conversation](https://github.com/Djelibeybi/openclaw_conversation) by [@Djelibeybi](https://github.com/Djelibeybi).**
> This is a fork modified to work with [Moltworker](https://github.com/cloudflare/moltworker) deployments, adding Cloudflare Access Service Token support to authenticate through the CF Access middleware layer.

## Features

- Voice and text conversations with AI-powered responses
- Control Home Assistant devices through natural language via [ha-mcp](https://homeassistant-ai.github.io/ha-mcp/)
- AI Task entity for structured data generation
- Cloudflare Access Service Token support for Moltworker deployments

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (⋮) → **Custom repositories**
3. Add `https://github.com/omribenami/moltworker_conversation` with category **Integration**
4. Search for "Moltworker Conversation" and install
5. Restart Home Assistant

### Manual

1. Copy `custom_components/moltworker_conversation/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Prerequisites

Before configuring this integration, you need:

1. **[Moltworker](https://github.com/cloudflare/moltworker)** deployed on Cloudflare Workers with a `MOLTBOT_GATEWAY_TOKEN` set
2. **[ha-mcp](https://homeassistant-ai.github.io/ha-mcp/)** server running (provides Home Assistant control to the agent)
3. **[mcporter](http://mcporter.dev/)** installed in the Moltworker container (add to `Dockerfile`)
4. **Cloudflare Access Service Token** — required if your worker is protected by Cloudflare Access

### Cloudflare Access Service Token

Moltworker runs behind Cloudflare Access, which requires a service token for Home Assistant to authenticate. To create one:

1. Go to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/) → **Access** → **Service Auth** → **Service Tokens**
2. Click **Create Service Token**, name it (e.g., `home-assistant`), and copy the **Client ID** and **Client Secret**
3. In your Access policy for the worker, add an **Allow** rule for this service token

See the [ha-mcp setup guide](docs/ha-mcp-setup.md) for additional setup details.

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** and search for **Moltworker Conversation**
3. Enter your Moltworker details:

| Field | Description |
|-------|-------------|
| **Moltworker URL** | Your worker URL (e.g., `https://your-worker.workers.dev`) |
| **Gateway Token** | Your `MOLTBOT_GATEWAY_TOKEN` secret |
| **Verify SSL** | Uncheck only for self-signed certificates (not needed for `workers.dev`) |
| **CF Access Client ID** | Cloudflare Access Service Token Client ID (required for Moltworker) |
| **CF Access Client Secret** | Cloudflare Access Service Token Client Secret |

### Agent Configuration

After adding the integration, add a conversation agent:

1. Click on the integration entry
2. Click **Add** under "Conversation agent"
3. Configure the agent:

| Option | Description |
|--------|-------------|
| **HA MCP Server URL** | Your ha-mcp server URL (e.g., `http://homeassistant.local:9583/private_XXXXX`) |
| **Prompt Template** | System prompt with Jinja2 template support |
| **Agent ID** | The OpenClaw agent to use (default: `main`) |
| **Session Key** | Optional key for session persistence |

> **Session Key:** Setting a session key (e.g., `agent:main:homeassistant`) keeps conversation context persistent across invocations.

## Usage

1. Go to **Settings** → **Voice Assistants**
2. Edit your assistant (or create a new one)
3. Select **Moltworker Conversation** as the **Conversation agent**

The agent uses [mcporter](http://mcporter.dev/) to communicate with Home Assistant via the [ha-mcp](https://homeassistant-ai.github.io/ha-mcp/) server. It can search for entities, control devices, manage automations, and more.

## Logging

Add to `configuration.yaml` to enable debug logging:

```yaml
logger:
  logs:
    custom_components.moltworker_conversation: debug
```

## License

This project is licensed under the [Universal Permissive License v1.0](LICENSE).

## Credits

- Forked from **[openclaw_conversation](https://github.com/Djelibeybi/openclaw_conversation)** by [@Djelibeybi](https://github.com/Djelibeybi)
- Originally based on [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation) by [@jekalmin](https://github.com/jekalmin)
- Uses [OpenClaw](https://github.com/openclaw/openclaw) via [Moltworker](https://github.com/cloudflare/moltworker) on Cloudflare Workers
