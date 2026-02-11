"""The Moltworker Conversation integration."""

from __future__ import annotations

import logging

import httpx

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_CF_ACCESS_CLIENT_ID,
    CONF_CF_ACCESS_CLIENT_SECRET,
    CONF_OPENCLAW_URL,
    CONF_VERIFY_SSL,
    DEFAULT_AGENT_ID,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CONVERSATION, Platform.AI_TASK]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type MoltworkerConfigEntry = ConfigEntry[None]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Moltworker Conversation."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MoltworkerConfigEntry) -> bool:
    """Set up Moltworker Conversation from a config entry."""
    base_url = entry.data[CONF_OPENCLAW_URL].rstrip("/")
    api_key = entry.data[CONF_API_KEY]
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)

    client = get_async_client(hass, verify_ssl=verify_ssl)

    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "x-openclaw-agent-id": DEFAULT_AGENT_ID,
    }

    # Include Cloudflare Access Service Token headers if configured
    # Strip accidental header-name prefixes (e.g. "CF-Access-Client-Id: value")
    cf_client_id = entry.data.get(CONF_CF_ACCESS_CLIENT_ID, "").strip()
    cf_client_secret = entry.data.get(CONF_CF_ACCESS_CLIENT_SECRET, "").strip()
    for prefix in ("CF-Access-Client-Id:", "CF-Access-Client-Secret:"):
        if cf_client_id.startswith(prefix):
            cf_client_id = cf_client_id[len(prefix) :].strip()
        if cf_client_secret.startswith(prefix):
            cf_client_secret = cf_client_secret[len(prefix) :].strip()
    if cf_client_id:
        headers["CF-Access-Client-Id"] = cf_client_id
    if cf_client_secret:
        headers["CF-Access-Client-Secret"] = cf_client_secret

    try:
        # Validate connectivity and auth by POSTing to chat completions endpoint
        # OpenClaw doesn't implement /v1/models, so we send a minimal request
        # A 401 means bad auth; connection/timeout means unreachable;
        # any other response (including 400 for bad payload) means success
        response = await client.post(
            f"{base_url}/v1/chat/completions",
            headers=headers,
            json={"model": "openclaw", "messages": []},
            timeout=10.0,
        )
        if response.status_code == 401:
            response.raise_for_status()
    except httpx.HTTPStatusError as err:
        if err.response.status_code == 401:
            _LOGGER.error("Invalid credentials for Moltworker")
            return False
        raise ConfigEntryNotReady(f"Failed to connect to Moltworker: {err}") from err
    except httpx.RequestError as err:
        raise ConfigEntryNotReady(f"Failed to connect to Moltworker: {err}") from err

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Moltworker Conversation."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
