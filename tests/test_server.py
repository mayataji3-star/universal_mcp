"""Tests for the universal send_sms routing service."""
from src.server import get_provider_requirements, run_send_sms

def test_routes_to_twilio():
    result = run_send_sms(
        provider="twilio",
        to="+962790000000",
        sender="Example",
        message="Hello",
    )

    assert result["success"] is True
    assert result["execution_mode"] == "simulation"
    assert result["provider_request"]["data"]["To"] == "+962790000000"
    assert result["canonical_response"]["provider"] == "twilio"
    assert result["canonical_response"]["status"] == "pending"


def test_routes_to_vonage():
    result = run_send_sms(
        provider="vonage",
        to="+962790000000",
        sender="Example",
        message="Hello",
        client_reference="request-001",
    )

    assert result["success"] is True
    assert result["provider_request"]["data"]["to"] == "962790000000"
    assert result["provider_request"]["data"]["client-ref"] == "request-001"
    assert result["canonical_response"]["provider"] == "vonage"
    assert result["canonical_response"]["status"] == "accepted"


def test_routes_to_messagebird():
    result = run_send_sms(
        provider="messagebird",
        to="+962790000000",
        sender="Example",
        message="Hello",
    )

    assert result["success"] is True
    assert result["provider_request"]["json"]["recipients"] == [
        "962790000000"
    ]
    assert result["canonical_response"]["provider"] == "messagebird"
    assert result["canonical_response"]["status"] == "sent"


def test_invalid_phone_returns_structured_error():
    result = run_send_sms(
        provider="twilio",
        to="0790000000",
        sender="Example",
        message="Hello",
    )

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"
    assert result["error"]["retryable"] is False


def test_unsupported_provider_returns_structured_error():
    result = run_send_sms(
        provider="unsupported-company",
        to="+962790000000",
        sender="Example",
        message="Hello",
    )

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"



def test_get_twilio_requirements():
    result = get_provider_requirements("twilio")

    assert result["success"] is True
    assert result["requirements"]["provider"] == "twilio"
    assert "to" in result["requirements"]["required_fields"]
    assert "sender" in result["requirements"]["required_fields"]
    assert "message" in result["requirements"]["required_fields"]


def test_get_messagebird_capabilities():
    result = get_provider_requirements("messagebird")

    assert result["success"] is True

    capabilities = result["requirements"]["provider_capabilities"]

    assert capabilities["multiple_recipients"] is True
    assert capabilities["canonical_tool_multiple_recipients"] is False


def test_get_requirements_rejects_unknown_provider():
    result = get_provider_requirements("unknown-provider")

    assert result["success"] is False
    assert result["error"]["code"] == "UNSUPPORTED_PROVIDER"
    assert result["error"]["retryable"] is False