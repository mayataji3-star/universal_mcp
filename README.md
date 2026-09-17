# Universal MCP Layer Viability Spike

This repository evaluates whether one MCP layer can expose a common business
operation across companies with different APIs.

The working spike exposes one MCP tool:

```text
send_sms
```

The tool supports three simulated provider adapters:

* Twilio
* Vonage
* MessageBird

## Important Limitation

This project does not make live provider API calls and does not send real SMS
messages.

It translates a canonical request into a provider-specific request and
translates a documented sample provider response into one canonical response.

The spike therefore tests the translation and routing architecture rather than
live SMS delivery.

## Architecture

```text
MCP client
    |
    v
send_sms
    |
    v
Canonical SMSRequest
    |
    +-- Twilio adapter
    |
    +-- Vonage adapter
    |
    +-- MessageBird adapter
    |
    v
Canonical SMSResponse
```

## How It Works

The MCP client calls one tool using a common request:

```json
{
  "provider": "twilio",
  "to": "+962790000000",
  "sender": "Example",
  "message": "Hello",
  "client_reference": "request-001"
}
```

The `provider` value selects the appropriate adapter.

The adapter translates the canonical request into the selected provider's
format. A documented-style sample provider response is then translated into the
canonical response.

The tool clearly returns:

```text
execution_mode: simulation
```

It also states that no external API call or real SMS was sent.

## Requirements

* Git
* Python 3.11 or newer

The spike was developed using Python 3.13.

## Installation

Clone the repository:

```powershell
git clone https://github.com/mayataji3-star/universal_mcp.git
cd universal_mcp
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

The execution-policy change applies only to the current PowerShell session.

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Automated Tests

Run:

```powershell
python -m pytest -v
```

All collected tests should pass.

The automated tests cover:

* Canonical request validation
* Twilio request translation
* Twilio response translation
* Vonage request translation
* Vonage success-response translation
* Vonage error normalization
* MessageBird request translation
* MessageBird response translation
* Provider routing
* Structured validation errors

## Run the MCP Smoke Test

Run:

```powershell
python scripts\smoke_test.py
```

The smoke test:

1. Starts the MCP server as a subprocess.
2. Connects using MCP stdio transport.
3. Initializes an MCP client session.
4. Lists the available tools.
5. Confirms that `send_sms` was discovered.
6. Calls `send_sms`.
7. Prints the simulated provider request and canonical response.
8. Confirms that the MCP call succeeded.

Successful output includes:

```text
Discovered MCP tools:
[
  "send_sms"
]
```

It should finish with:

```text
MCP smoke test passed.
```

## Run the MCP Server Directly

Run:

```powershell
python -m src.server
```

The server uses stdio transport and waits for an MCP client.

The terminal may appear to wait without printing anything. This is expected
because the server is waiting for MCP protocol input.

Press `Ctrl+C` to stop the server.

## Example Canonical Request

```json
{
  "provider": "messagebird",
  "to": "+962790000000",
  "sender": "Example",
  "message": "Hello from the universal MCP layer",
  "client_reference": "request-001"
}
```

## Example Canonical Response

```json
{
  "provider": "messagebird",
  "message_id": "MESSAGEBIRD_SIMULATED_001",
  "status": "sent",
  "to": "+962790000000",
  "provider_status": "sent",
  "error": null
}
```

## Project Structure

```text
universal_mcp/
├── docs/
│   ├── provider_mapping.md
│   ├── smoke_test_output.txt
│   └── spike_execution.md
├── scripts/
│   └── smoke_test.py
├── src/
│   ├── __init__.py
│   ├── schemas.py
│   ├── server.py
│   └── adapters/
│       ├── __init__.py
│       ├── twilio.py
│       ├── vonage.py
│       └── messagebird.py
├── tests/
│   ├── __init__.py
│   ├── test_adapters.py
│   └── test_server.py
├── .gitignore
├── ASSESSMENT.md
├── INITIAL_PREDICTION.md
├── README.md
└── requirements.txt
```

## Provider Mapping

The provider comparison and field mappings are documented in:

```text
docs/provider_mapping.md
```

## Execution Evidence

The executed-versus-documentation boundary is recorded in:

```text
docs/spike_execution.md
```

The saved MCP smoke-test output is located in:

```text
docs/smoke_test_output.txt
```

## Evidence Boundary

### Executed Locally

The following behavior was executed:

* Schema validation
* Three provider request translations
* Three provider response translations
* Provider routing
* Error normalization
* MCP stdio server startup
* MCP tool discovery
* MCP tool invocation
* Canonical response retrieval

### Documentation-Only

The following behavior was not executed:

* Provider authentication
* Live external API requests
* Real SMS delivery
* Real delivery callbacks
* Provider billing
* Provider rate limits
* Production retries
* Provider outages

## Security

No API keys or provider credentials should be committed to this repository.

The `.gitignore` file excludes:

```text
.env
.venv/
```

If live credentials are added in future work, they must be loaded from a secure
environment or secret-management system.

## Current Result

The spike demonstrates that one MCP tool can route a common SMS operation across
three differently shaped provider APIs.

It also demonstrates that each provider still requires its own mapping,
response normalization, error handling, testing, and maintenance.
