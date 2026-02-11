"""The exceptions used by OpenClaw Conversation."""

from homeassistant.exceptions import HomeAssistantError


class ParseArgumentsFailed(HomeAssistantError):
    """When parse arguments failed."""

    def __init__(self, arguments: str) -> None:
        """Initialize error."""
        super().__init__(
            self,
            f"failed to parse arguments `{arguments}`. Increase maximum token to avoid the issue.",
        )
        self.arguments = arguments

    def __str__(self) -> str:
        """Return string representation."""
        return f"failed to parse arguments `{self.arguments}`. Increase maximum token to avoid the issue."


class TokenLengthExceededError(HomeAssistantError):
    """When openai return 'length' as 'finish_reason'."""

    def __init__(self, token: int) -> None:
        """Initialize error."""
        super().__init__(
            self,
            f"token length(`{token}`) exceeded. Increase maximum token to avoid the issue.",
        )
        self.token = token

    def __str__(self) -> str:
        """Return string representation."""
        return f"token length(`{self.token}`) exceeded. Increase maximum token to avoid the issue."
