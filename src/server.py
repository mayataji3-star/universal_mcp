"""Universal SMS MCP server.

The spike operates in simulation mode. It translates canonical requests and
documented sample responses without sending real SMS messages.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from src.adapters import messagebird, twilio, vonage
from src.schemas import SMSRequest


mcp = FastMCP("Universal SMS Layer")

ADAPTERS = {
    "twilio": twilio,
    "vonage": vonage,
    "messagebird": messagebird,
}


def sample_provider_response(provider: str, to: str) -> dict[str, Any]:
    """Return a documented-style sample response for local simulation."""

    if provider == "twilio":
        return {
            "sid": "SM_SIMULATED_001",
            "status": "queued",
            "to": to,
            "error_code": None,
            "error_message": None,
        }

    if provider == "vonage":
        return {
            "message-count": "1",
            "messages": [
                {
                    "to": to.lstrip("+"),
                    "message-id": "VONAGE_SIMULATED_001",
                    "status": "0",
                }
            ],
        }

    if provider == "messagebird":
        return {
            "id": "MESSAGEBIRD_SIMULATED_001",
            "recipients": {
                "items": [
                    {
                        "recipient": to.lstrip("+"),
                        "status": "sent",
                    }
                ]
            },
        }

    raise ValueError(f"Unsupported provider: {provider}")


def run_send_sms(
    provider: str,
    to: str,
    sender: str,
    message: str,
    client_reference: str | None = None,
) -> dict[str, Any]:
    """Run the canonical request through the selected provider adapter."""

    try:
        canonical_request = SMSRequest(
            provider=provider,
            to=to,
            sender=sender,
            message=message,
            client_reference=client_reference,
        )
    except ValidationError as exc:
        return {
            "success": False,
            "execution_mode": "simulation",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The canonical SMS request is invalid.",
                "retryable": False,
                "details": exc.errors(
                    include_url=False,
                    include_context=False,
                ),
            },
        }

    adapter = ADAPTERS[canonical_request.provider]

    provider_request = adapter.build_request(canonical_request)
    provider_response = sample_provider_response(
        canonical_request.provider,
        canonical_request.to,
    )

    canonical_response = adapter.parse_response(
        provider_response,
        canonical_request,
    )

    return {
        "success": canonical_response.error is None,
        "execution_mode": "simulation",
        "notice": "No external API call or real SMS was sent.",
        "provider_request": provider_request,
        "sample_provider_response": provider_response,
        "canonical_response": canonical_response.model_dump(),
    }

@mcp.tool()
def get_requirements(provider: str) -> dict[str, Any]:
    """Get required fields, rules, and capabilities for an SMS provider.

    Call this tool before send_sms when the selected provider's requirements
    are unknown. Supported providers are twilio, vonage, and messagebird.
    """

    return get_provider_requirements(provider)

@mcp.tool()
def send_sms(
    provider: str,
    to: str,
    sender: str,
    message: str,
    client_reference: str | None = None,
) -> dict[str, Any]:
    """Prepare an SMS for Twilio, Vonage, or MessageBird.

    Use this tool when the user wants to send an SMS through one of the
    supported providers. The provider must be twilio, vonage, or messagebird.
    The recipient number must begin with '+' and include the country code.

    This assessment spike runs in simulation mode. It translates the request
    into the selected provider's format and normalizes a sample provider
    response. It does not contact an external API or send a real SMS.
    """

    return run_send_sms(
        provider=provider,
        to=to,
        sender=sender,
        message=message,
        client_reference=client_reference,
    )




PROVIDER_REQUIREMENTS = {
    "twilio": {
        "provider": "twilio",
        "required_fields": [
            "to",
            "sender",
            "message",
        ],
        "optional_fields": [
            "client_reference",
        ],
        "recipient_format": "E.164 format beginning with '+'",
        "sender_rules": (
            "Use a Twilio-owned telephone number, approved sender ID, "
            "or configured messaging service."
        ),
        "lifecycle": (
            "The initial response may be queued. Final delivery can be "
            "reported later through a status callback."
        ),
    },
    "vonage": {
        "provider": "vonage",
        "required_fields": [
            "to",
            "sender",
            "message",
        ],
        "optional_fields": [
            "client_reference",
        ],
        "recipient_format": "International number beginning with '+'",
        "sender_rules": (
            "The sender may be a permitted telephone number or "
            "alphanumeric sender ID."
        ),
        "lifecycle": (
            "A successful initial status means the request was accepted, "
            "not necessarily delivered."
        ),
    },
    "messagebird": {
        "provider": "messagebird",
        "required_fields": [
            "to",
            "sender",
            "message",
        ],
        "optional_fields": [
            "client_reference",
        ],
        "recipient_format": "International number beginning with '+'",
        "sender_rules": (
            "The originator may be a telephone number or an alphanumeric "
            "sender ID, subject to destination-country restrictions."
        ),
        "lifecycle": (
            "Recipient delivery status may be updated after the initial "
            "response."
        ),
        "provider_capabilities": {
            "multiple_recipients": True,
            "canonical_tool_multiple_recipients": False,
        },
    },
}




def get_provider_requirements(provider: str) -> dict[str, Any]:
    """Return requirements and capabilities for one SMS provider."""

    normalized_provider = provider.strip().lower()

    requirements = PROVIDER_REQUIREMENTS.get(normalized_provider)

    if requirements is None:
        return {
            "success": False,
            "error": {
                "code": "UNSUPPORTED_PROVIDER",
                "message": (
                    f"Provider '{provider}' is not supported. "
                    "Supported providers are twilio, vonage, and messagebird."
                ),
                "retryable": False,
            },
        }

    return {
        "success": True,
        "requirements": requirements,
    }

if __name__ == "__main__":
    mcp.run()