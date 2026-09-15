"""Vonage request and response adapter."""

from typing import Any

from src.schemas import SMSError, SMSRequest, SMSResponse


VONAGE_ENDPOINT = "https://rest.nexmo.com/sms/json"

VONAGE_STATUS_MAP = {
    "0": "accepted",
}

VONAGE_ERROR_MESSAGES = {
    "1": "Throttled",
    "2": "Missing parameter",
    "3": "Invalid parameter",
    "4": "Invalid credentials",
    "5": "Internal error",
    "6": "Invalid message",
    "9": "Partner quota exceeded",
    "15": "Invalid sender address",
}


def build_request(request: SMSRequest) -> dict[str, Any]:
    """Translate a canonical request into a Vonage request description."""

    data = {
        "to": request.to.lstrip("+"),
        "from": request.sender,
        "text": request.message,
    }

    if request.client_reference:
        data["client-ref"] = request.client_reference

    return {
        "method": "POST",
        "url": VONAGE_ENDPOINT,
        "encoding": "application/x-www-form-urlencoded",
        "data": data,
    }


def parse_response(
    payload: dict[str, Any],
    original_request: SMSRequest,
) -> SMSResponse:
    """Translate a Vonage response into the canonical response."""

    messages = payload.get("messages", [])

    if not messages:
        return SMSResponse(
            provider="vonage",
            status="failed",
            to=original_request.to,
            provider_status="missing_response",
            error=SMSError(
                code="INVALID_PROVIDER_RESPONSE",
                message="Vonage returned no message result.",
                retryable=False,
                provider_details=payload,
            ),
        )

    message = messages[0]
    provider_status = str(message.get("status", "unknown"))

    if provider_status == "0":
        return SMSResponse(
            provider="vonage",
            message_id=message.get("message-id"),
            status=VONAGE_STATUS_MAP[provider_status],
            to=original_request.to,
            provider_status=provider_status,
            error=None,
        )

    return SMSResponse(
        provider="vonage",
        message_id=message.get("message-id"),
        status="failed",
        to=original_request.to,
        provider_status=provider_status,
        error=SMSError(
            code=f"VONAGE_{provider_status}",
            message=VONAGE_ERROR_MESSAGES.get(
                provider_status,
                "Unknown Vonage error",
            ),
            retryable=provider_status in {"1", "5"},
            provider_details=message,
        ),
    )