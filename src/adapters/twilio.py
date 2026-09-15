"""Twilio request and response adapter."""

from typing import Any

from src.schemas import SMSRequest, SMSResponse


TWILIO_ENDPOINT = (
    "https://api.twilio.com/2010-04-01/"
    "Accounts/{account_sid}/Messages.json"
)

TWILIO_STATUS_MAP = {
    "accepted": "accepted",
    "scheduled": "pending",
    "queued": "pending",
    "sending": "pending",
    "sent": "sent",
    "delivered": "delivered",
    "failed": "failed",
    "undelivered": "failed",
    "canceled": "failed",
}


def build_request(request: SMSRequest) -> dict[str, Any]:
    """Translate a canonical request into a Twilio request description."""

    return {
        "method": "POST",
        "url": TWILIO_ENDPOINT,
        "encoding": "application/x-www-form-urlencoded",
        "data": {
            "To": request.to,
            "From": request.sender,
            "Body": request.message,
        },
    }


def parse_response(
    payload: dict[str, Any],
    original_request: SMSRequest,
) -> SMSResponse:
    """Translate a Twilio response into the canonical response."""

    provider_status = str(payload.get("status", "unknown"))
    canonical_status = TWILIO_STATUS_MAP.get(provider_status, "pending")

    return SMSResponse(
        provider="twilio",
        message_id=payload.get("sid"),
        status=canonical_status,
        to=str(payload.get("to", original_request.to)),
        provider_status=provider_status,
        error=None,
    )