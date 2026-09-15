"""Canonical request and response schemas for the universal SMS tool."""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


ProviderName = Literal["twilio", "vonage", "messagebird"]
CanonicalStatus = Literal[
    "accepted",
    "pending",
    "sent",
    "delivered",
    "failed",
]


class SMSRequest(BaseModel):
    """Provider-independent request accepted by the send_sms MCP tool."""

    provider: ProviderName

    to: str = Field(
        min_length=8,
        description="Recipient telephone number in international format.",
    )

    sender: str = Field(
        min_length=1,
        max_length=20,
        description="Sender telephone number or alphanumeric sender ID.",
    )

    message: str = Field(
        min_length=1,
        description="Text content of the SMS message.",
    )

    client_reference: str | None = Field(
        default=None,
        description="Optional reference supplied by the caller.",
    )

    @field_validator("to")
    @classmethod
    def validate_recipient(cls, value: str) -> str:
        """Require a simple international telephone-number format."""

        cleaned = value.strip()

        if not cleaned.startswith("+"):
            raise ValueError(
                "The recipient number must start with '+' and include "
                "the country code."
            )

        if not cleaned[1:].isdigit():
            raise ValueError(
                "The recipient number must contain only '+' followed by digits."
            )

        return cleaned


class SMSError(BaseModel):
    """Normalized error returned by any provider adapter."""

    code: str
    message: str
    retryable: bool = False
    provider_details: dict[str, Any] | None = None


class SMSResponse(BaseModel):
    """Provider-independent response returned by the send_sms MCP tool."""

    provider: ProviderName
    message_id: str | None = None
    status: CanonicalStatus
    to: str
    provider_status: str | None = None
    error: SMSError | None = None