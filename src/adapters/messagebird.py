"""MessageBird request and response adapter."""

from typing import Any

from src.schemas import SMSError, SMSRequest, SMSResponse


MESSAGEBIRD_ENDPOINT = "https://rest.messagebird.com/messages"

MESSAGEBIRD_STATUS_MAP = {
    "scheduled": "pending",
    "buffered": "pending",
    "sent": "sent",
    "delivered": "delivered",
    "delivery_failed": "failed",
    "expired": "failed",
}


def build_request(request: SMSRequest) -> dict[str, Any]:
    """Translate a canonical request into a MessageBird request."""

    data: dict[str, Any] = {
        "originator": request.sender,
        "recipients": [request.to.lstrip("+")],
        "body": request.message,
    }

    if request.client_reference:
        data["reference"] = request.client_reference

    return {
        "method": "POST",
        "url": MESSAGEBIRD_ENDPOINT,
        "encoding": "application/json",
        "json": data,
    }


def parse_response(
    payload: dict[str, Any],
    original_request: SMSRequest,
) -> SMSResponse:
    """Translate a MessageBird response into the canonical response."""

    recipient_data = payload.get("recipients", {})
    items = recipient_data.get("items", [])

    if not items:
        return SMSResponse(
            provider="messagebird",
            message_id=payload.get("id"),
            status="failed",
            to=original_request.to,
            provider_status="missing_response",
            error=SMSError(
                code="INVALID_PROVIDER_RESPONSE",
                message="MessageBird returned no recipient result.",
                retryable=False,
                provider_details=payload,
            ),
        )

    recipient = items[0]
    provider_status = str(recipient.get("status", "unknown"))
    canonical_status = MESSAGEBIRD_STATUS_MAP.get(
        provider_status,
        "pending",
    )

    error = None

    if canonical_status == "failed":
        error = SMSError(
            code=str(
                recipient.get(
                    "statusErrorCode",
                    "MESSAGEBIRD_DELIVERY_FAILED",
                )
            ),
            message=str(
                recipient.get(
                    "statusReason",
                    "Message delivery failed.",
                )
            ),
            retryable=False,
            provider_details=recipient,
        )

    return SMSResponse(
        provider="messagebird",
        message_id=payload.get("id"),
        status=canonical_status,
        to=original_request.to,
        provider_status=provider_status,
        error=error,
    )