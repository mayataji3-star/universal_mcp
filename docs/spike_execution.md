# Spike Execution Record

## Scope

The spike tested whether one canonical MCP tool could route the same business
operation to three providers with different API structures.

The selected operation was sending an SMS. The selected providers were:

* Twilio
* Vonage
* MessageBird

The spike was designed to test the translation and routing architecture without
requiring live provider accounts or credentials.

## What Was Implemented

The following components were implemented:

* A canonical `SMSRequest` schema
* A canonical `SMSResponse` schema
* A normalized `SMSError` schema
* A Twilio adapter
* A Vonage adapter
* A MessageBird adapter
* One MCP tool named `send_sms`
* Automated provider-adapter tests
* Automated provider-routing tests
* An MCP stdio smoke test

Each provider adapter implements two transformations:

```text
Canonical request -> Provider-specific request
Provider response -> Canonical response
```

## Canonical Request

The MCP tool accepts one common request format:

```json
{
  "provider": "twilio",
  "to": "+962790000000",
  "sender": "Example",
  "message": "Hello from the universal MCP layer",
  "client_reference": "request-001"
}
```

The same canonical structure can be used with Twilio, Vonage, or MessageBird by
changing the `provider` value.

## Canonical Response

Provider responses are normalized into one common response structure:

```json
{
  "provider": "twilio",
  "message_id": "SM_SIMULATED_001",
  "status": "pending",
  "to": "+962790000000",
  "provider_status": "queued",
  "error": null
}
```

## What Was Executed

The following behavior was executed locally:

* Canonical request-schema validation
* Rejection of invalid telephone-number formats
* Canonical-to-Twilio request translation
* Canonical-to-Vonage request translation
* Canonical-to-MessageBird request translation
* Twilio-to-canonical response translation
* Vonage-to-canonical response translation
* MessageBird-to-canonical response translation
* Provider selection through one `send_sms` operation
* Normalization of provider statuses
* Normalization of provider errors
* Structured validation-error responses
* MCP server startup using stdio
* MCP client connection to the server
* MCP tool discovery
* MCP `send_sms` tool invocation
* Canonical response retrieval through the MCP client

The automated tests were executed with:

```powershell
python -m pytest -v
```

The end-to-end MCP smoke test was executed with:

```powershell
python scripts\smoke_test.py
```

The smoke test discovered the following MCP tool:

```text
send_sms
```

The smoke test then called `send_sms` using the Twilio provider and successfully
received a simulated canonical response.

The saved smoke-test output is available in:

```text
docs/smoke_test_output.txt
```

## What Was Not Executed

No live provider API calls were made.

The spike did not:

* Authenticate with Twilio
* Authenticate with Vonage
* Authenticate with MessageBird
* Send a real SMS
* Use real API keys
* Use real customer credentials
* Receive a real delivery callback
* Test actual provider rate limits
* Test provider outages
* Verify real provider billing
* Verify production retry behavior
* Verify country-specific SMS regulations
* Verify final handset delivery

Provider requests and responses were based on publicly documented API
structures and example payloads.

## Why Simulation Was Used

The assignment allowed documented request and response examples instead of live
provider credentials.

Simulation isolated the main question being investigated: whether one canonical
MCP tool could translate between different provider API structures.

It also avoided spending the spike on:

* Account registration
* Sandbox approval
* Billing configuration
* Telephone-number verification
* Regulatory approval
* Credential management

## Provider Differences Observed

Although the providers perform the same business action, their APIs differ in
several ways.

### Field names

The same concepts use different names:

| Canonical concept | Twilio | Vonage       | MessageBird  |
| ----------------- | ------ | ------------ | ------------ |
| Recipient         | `To`   | `to`         | `recipients` |
| Sender            | `From` | `from`       | `originator` |
| Message           | `Body` | `text`       | `body`       |
| Message ID        | `sid`  | `message-id` | `id`         |

### Request structures

Twilio and Vonage use form-style fields in the spike, while MessageBird uses a
JSON structure containing a recipients array.

### Response structures

Twilio returns a message object directly.

Vonage returns a `messages` array even when only one SMS is sent.

MessageBird nests recipient status information inside a recipients object.

### Status formats

Twilio and MessageBird use textual statuses.

Vonage uses numeric status codes. For example, `"0"` represents successful
acceptance.

### Error formats

Every provider represents errors differently. The adapters must translate these
differences into the common `SMSError` structure.

### Lifecycle differences

An initial successful API response does not necessarily mean that the SMS was
delivered. A provider may initially return `queued`, `accepted`, or `sent` and
provide the final delivery result later.

## Declarative Mapping Versus Custom Code

Some differences could be represented using mapping dictionaries, including:

* Request field names
* Response field names
* Status translations
* Endpoint addresses

Other differences required provider-specific code, including:

* Reading the first item from Vonage's nested `messages` array
* Reading MessageBird's nested recipient information
* Handling empty provider response arrays
* Translating numeric error codes
* Determining whether an error is retryable
* Converting one canonical recipient into MessageBird's recipients array

This is an important finding. Mapping tables reduce adapter code, but they
cannot represent every provider difference.

## Spike Result

The spike demonstrated that one MCP tool can accept a canonical SMS request,
route it through one of three provider-specific adapters, and return a
normalized response.

The spike also demonstrated that onboarding a provider is not completely
automatic. Every provider requires:

* API-documentation review
* Field mapping
* Authentication configuration
* Request translation
* Response translation
* Status normalization
* Error normalization
* Tests
* Ongoing maintenance

## Preliminary Conclusion

The spike supports the preliminary conclusion that a universal MCP layer is
viable for a clearly defined business operation.

However, the layer cannot accept an arbitrary API and automatically understand
its business meaning. Every provider still requires a reviewed and tested
adapter.

The most realistic architecture is a hybrid consisting of:

* A canonical model for common functionality
* One adapter per provider
* Provider capability metadata
* Optional provider-specific extensions
* A controlled passthrough mechanism for functionality outside the canonical
  model
