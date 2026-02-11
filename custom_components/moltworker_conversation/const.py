"""Constants for the Moltworker Conversation integration."""

DOMAIN = "moltworker_conversation"
DEFAULT_NAME = "Moltworker Conversation"
DEFAULT_CONVERSATION_NAME = "Moltworker Conversation"
DEFAULT_AI_TASK_NAME = "Moltworker AI Task"

# Config flow fields
CONF_OPENCLAW_URL = "openclaw_url"
CONF_HA_MCP_URL = "ha_mcp_url"
CONF_SESSION_KEY = "session_key"
CONF_AGENT_ID = "agent_id"
CONF_VERIFY_SSL = "verify_ssl"

# Cloudflare Access Service Token (for moltworker deployments behind CF Access)
CONF_CF_ACCESS_CLIENT_ID = "cf_access_client_id"
CONF_CF_ACCESS_CLIENT_SECRET = "cf_access_client_secret"

# Defaults
DEFAULT_AGENT_ID = "main"
DEFAULT_SESSION_KEY = ""
DEFAULT_VERIFY_SSL = True

# Events
EVENT_CONVERSATION_FINISHED = "moltworker_conversation.conversation.finished"

# Prompt configuration
CONF_PROMPT = "prompt"
DEFAULT_PROMPT = """You are a voice assistant for Home Assistant.

Answer in plain text only.
Respond naturally as a voice assistant.
Prefer a single sentence; use up to 2-3 sentences only when truly necessary.

You have access to Home Assistant via mcporter and the ha-mcp server. To control devices, search entities, or manage automations, use:

mcporter call {{ha_mcp_url}}.<tool> --allow-http [args]

Key tools:
- ha_search_entities query="..." — find entities
- ha_call_service domain=X service=Y entity_id=Z — control devices
- ha_config_list_areas — list rooms
- ha_config_get_automation / ha_config_set_automation — view/edit automations

When asked to control a device, search for it first if you don't know the entity_id, then call the appropriate service.

For general knowledge questions not related to the home, answer truthfully using internal knowledge only.

{{user_input.extra_system_prompt | default('', true)}}
"""

# Context management
CONF_CONTEXT_THRESHOLD = "context_threshold"
DEFAULT_CONTEXT_THRESHOLD = 13000
CONTEXT_TRUNCATE_STRATEGIES = [{"key": "clear", "label": "Clear All Messages"}]
CONF_CONTEXT_TRUNCATE_STRATEGY = "context_truncate_strategy"
DEFAULT_CONTEXT_TRUNCATE_STRATEGY = CONTEXT_TRUNCATE_STRATEGIES[0]["key"]
