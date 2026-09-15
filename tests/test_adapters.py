"""Tests for SMS provider request and response adapters."""

from src.adapters import messagebird, twilio, vonage
from src.schemas import SMSRequest


def make_request(provider: str) -> SMSRequest:
    """Create a canonical request for adapter tests."""

    return SMSRequest(
        provider=provider,
        to="+962790000000",
        sender="Example",
        message="Hello from the universal MCP layer",
        client_reference="request-001",
    )


def test_twilio_build_request():
    request = make_request("twilio")

    result = twilio.build_request(request)

    assert result["method"] == "POST"
    assert result["encoding"] == "application/x-www-form-urlencoded"
    assert result["data"]["To"] == "+962790000000"
    assert result["data"]["From"] == "Example"
    assert result["data"]["Body"] == "Hello from the universal MCP layer"


def test_twilio_parse_response():
    request = make_request("twilio")

    provider_response = {
        "sid": "SM123",
        "status": "queued",
        "to": "+962790000000",
        "error_code": None,
        "error_message": None,
    }

    result = twilio.parse_response(provider_response, request)

    assert result.provider == "twilio"
    assert result.message_id == "SM123"
    assert result.status == "pending"
    assert result.provider_status == "queued"
    assert result.error is None


def test_vonage_build_request():
    request = make_request("vonage")

    result = vonage.build_request(request)

    assert result["method"] == "POST"
    assert result["data"]["to"] == "962790000000"
    assert result["data"]["from"] == "Example"
    assert result["data"]["text"] == "Hello from the universal MCP layer"
    assert result["data"]["client-ref"] == "request-001"


def test_vonage_parse_success_response():
    request = make_request("vonage")

    provider_response = {
        "message-count": "1",
        "messages": [
            {
                "to": "962790000000",
                "message-id": "0A00000012345678",
                "status": "0",
            }
        ],
    }

    result = vonage.parse_response(provider_response, request)

    assert result.provider == "vonage"
    assert result.message_id == "0A00000012345678"
    assert result.status == "accepted"
    assert result.provider_status == "0"
    assert result.error is None


def test_vonage_parse_error_response():
    request = make_request("vonage")

    provider_response = {
        "message-count": "1",
        "messages": [
            {
                "status": "1",
                "error-text": "Throttled",
            }
        ],
    }

    result = vonage.parse_response(provider_response, request)

    assert result.provider == "vonage"
    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == "VONAGE_1"
    assert result.error.retryable is True


def test_messagebird_build_request():
    request = make_request("messagebird")

    result = messagebird.build_request(request)

    assert result["method"] == "POST"
    assert result["encoding"] == "application/json"
    assert result["json"]["originator"] == "Example"
    assert result["json"]["recipients"] == ["962790000000"]
    assert result["json"]["body"] == "Hello from the universal MCP layer"
    assert result["json"]["reference"] == "request-001"


def test_messagebird_parse_response():
    request = make_request("messagebird")

    provider_response = {
        "id": "messagebird-id-123",
        "recipients": {
            "items": [
                {
                    "recipient": 962790000000,
                    "status": "sent",
                }
            ]
        },
    }

    result = messagebird.parse_response(provider_response, request)

    assert result.provider == "messagebird"
    assert result.message_id == "messagebird-id-123"
    assert result.status == "sent"
    assert result.provider_status == "sent"
    assert result.error is None


def test_messagebird_missing_recipient_result():
    request = make_request("messagebird")

    provider_response = {
        "id": "messagebird-id-123",
        "recipients": {
            "items": [],
        },
    }

    result = messagebird.parse_response(provider_response, request)

    assert result.status == "failed"
    assert result.error is not None
    assert result.error.code == "INVALID_PROVIDER_RESPONSE"