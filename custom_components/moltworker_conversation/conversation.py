"""Moltworker Conversation agent entity."""

from __future__ import annotations

import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.components.conversation import (
    ChatLog,
    ConversationEntity,
    ConversationEntityFeature,
    ConversationInput,
    ConversationResult,
    async_get_chat_log,
)
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import MATCH_ALL
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import intent, llm, template
from homeassistant.helpers.chat_session import async_get_chat_session
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import MoltworkerConfigEntry
from .const import (
    CONF_HA_MCP_URL,
    CONF_PROMPT,
    DEFAULT_PROMPT,
    DOMAIN,
    EVENT_CONVERSATION_FINISHED,
)
from .entity import MoltworkerBaseLLMEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry: MoltworkerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Moltworker Conversation entities."""
    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != "conversation":
            continue

        async_add_entities(
            [MoltworkerAgentEntity(config_entry, subentry)],
            config_subentry_id=subentry.subentry_id,
        )


class MoltworkerAgentEntity(
    ConversationEntity,
    conversation.AbstractConversationAgent,
    MoltworkerBaseLLMEntity,
):
    """Moltworker conversation agent."""

    _attr_supports_streaming = True
    _attr_supported_features = ConversationEntityFeature.CONTROL

    def __init__(
        self,
        entry: MoltworkerConfigEntry,
        subentry: ConfigSubentry,
    ) -> None:
        """Initialize the agent."""
        super().__init__(entry, subentry)

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process a sentence."""
        with (
            async_get_chat_session(self.hass, user_input.conversation_id) as session,
            async_get_chat_log(self.hass, session, user_input) as chat_log,
        ):
            return await self._async_handle_message(user_input, chat_log)

    async def _async_handle_message(
        self,
        user_input: ConversationInput,
        chat_log: ChatLog,
    ) -> ConversationResult:
        """Call the API."""
        llm_context = user_input.as_llm_context(DOMAIN)
        system_prompt = self._build_system_prompt(llm_context, user_input)
        chat_log.content[0] = conversation.SystemContent(content=system_prompt)

        try:
            await self._async_handle_chat_log(
                chat_log,
                llm_context=llm_context,
            )
        except HomeAssistantError as err:
            _LOGGER.error(err, exc_info=err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"Something went wrong: {err}",
            )
            return conversation.ConversationResult(
                response=intent_response, conversation_id=user_input.conversation_id
            )

        self.hass.bus.async_fire(
            EVENT_CONVERSATION_FINISHED,
            {
                "user_input": user_input,
                "messages": [c.as_dict() for c in chat_log.content],
                "agent_id": self.subentry.subentry_id,
            },
        )

        intent_response = intent.IntentResponse(language=user_input.language)
        last_content = chat_log.content[-1]
        if isinstance(last_content, conversation.AssistantContent):
            intent_response.async_set_speech(last_content.content or "")
        else:
            intent_response.async_set_speech("")

        return ConversationResult(
            response=intent_response,
            conversation_id=chat_log.conversation_id,
            continue_conversation=chat_log.continue_conversation,
        )

    def _build_system_prompt(
        self,
        llm_context: llm.LLMContext,
        user_input: ConversationInput,
    ) -> str:
        """Build system prompt."""
        raw_prompt = self.subentry.data.get(CONF_PROMPT, DEFAULT_PROMPT)
        ha_mcp_url = self.subentry.data.get(CONF_HA_MCP_URL, "")

        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
                "ha_mcp_url": ha_mcp_url,
                "current_device_id": llm_context.device_id,
                "user_input": user_input,
            },
            parse_result=False,
        )
