# SMS Provider API Mapping

## Purpose

This document compares three publicly documented APIs that perform the same
business action: sending an SMS message.

The providers are:

- Twilio
- Vonage
- MessageBird

The comparison will be used to design one canonical `send_sms` MCP tool and
three provider-specific adapters.

No live SMS messages were sent. This mapping is based on the providers'
published documentation and example payloads.

---

## Canonical Request

The universal MCP tool will initially accept this common request:

```json
{
  "provider": "twilio",
  "to": "+962790000000",
  "sender": "Example",
  "message": "Hello from the universal MCP layer",
  "client_reference": "request-001"
}