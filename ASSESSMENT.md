# Universal MCP Layer Viability Assessment

## Executive Summary

The proposed universal MCP layer is **viable under specific conditions**.

The working spike demonstrated that one canonical MCP tool can expose the same
business operation across providers with different API structures. A shared
`send_sms` tool routed canonical requests through Twilio, Vonage, and
MessageBird adapters and normalized their different response formats into one
canonical response.

However, the layer cannot accept an arbitrary API and automatically understand
its business meaning. Every provider still requires a reviewed and tested
adapter covering authentication, field mapping, request and response
translation, status normalization, error handling, lifecycle behavior,
capability differences, and ongoing maintenance.

The recommended architecture is a domain-specific hybrid consisting of:

- A stable canonical model for common functionality
- One tested adapter per provider
- Provider requirement and capability discovery
- Structured canonical errors
- Idempotency controls for write operations
- Optional provider-specific extensions
- A controlled passthrough mechanism for unsupported functionality
- Automated contract, routing, and regression tests

The original estimate of **24–40 working hours to onboard an additional
provider** remains reasonable for a well-documented API of moderate complexity.
Complex authentication, asynchronous workflows, regulatory requirements, poor
documentation, or major capability differences would increase this estimate.

The conclusion is therefore not that one MCP tool works automatically with
every API. The conclusion is that one stable MCP interface can serve multiple
providers when provider-specific complexity is deliberately handled behind
that interface.

## Initial Prediction

The prediction recorded before the research and implementation is preserved
unchanged in [INITIAL_PREDICTION.md](INITIAL_PREDICTION.md).

The initial prediction was that the system would be **viable under specific
conditions**, with an estimated onboarding cost of **24–40 working hours per
additional company**.

The completed research and spike support that prediction.

---

## Part 1 — Existing Solutions and Architecture

### Research Method

This part is based on documentation research. The vendor platforms and ACORD
standards discussed below were not installed or executed as part of the spike.
The purpose of this research was to identify how existing systems solve the
problem of exposing one interface over multiple different APIs.

### 1. Domain Standards: ACORD

ACORD provides insurance data standards for areas including Property and
Casualty, Life and Annuity, and Global Reinsurance and Large Commercial
insurance. Its Reference Architecture includes business processes, product
models, an Information Model, a Data Model, and a Capability Model.

This makes ACORD an important starting point for an insurance canonical model.
The universal layer should evaluate ACORD concepts before inventing a new
insurance vocabulary. However, ACORD is broader than the schema of one MCP
operation such as `create_policy`. A project would still need to select the
relevant concepts and design a smaller operational request and response model.

ACORD also does not eliminate provider adapters. Insurance companies may use
different ACORD versions, subsets, workflows, interpretations, or completely
custom APIs. Each company would still require mapping, authentication,
workflow handling, testing, and maintenance.

Some detailed ACORD packages and implementation resources may require
membership or participation in an ACORD Standards program. Licensing and
access requirements would therefore need to be confirmed before commercial
use.

**Finding:** ACORD can provide the semantic foundation for an insurance
canonical model, but it does not make onboarding every insurance company
automatic.

Sources:

- [ACORD Data Standards](https://www.acord.org/standards-architecture/acord-data-standards)
- [ACORD Property and Casualty Data Standards](https://www.acord.org/standards-architecture/acord-data-standards/Property_Casualty_Data_Standards)
- [ACORD Reference Architecture](https://www.acord.org/standards-architecture/reference-architecture)
- [ACORD Framework Overview](https://www.acord.org/staticfiles/reference_architecture/overview/story_html5.html)

### 2. Unified API Platforms

Merge, Apideck, Nango, and Paragon demonstrate that multiple providers can be
placed behind a common interface. Their general architecture is:

1. The client uses a common model.
2. The platform selects the correct provider integration.
3. Provider-specific code translates the common request.
4. The platform applies the provider's authentication and calls its API.
5. The response is translated back into a common model.

This reduces work for the client but does not remove provider-specific work
from the integration platform.

#### Merge

Merge exposes Common Models and supplements them with Remote Data, Field
Mapping, Remote Field Classes, and Authenticated Passthrough Requests. These
features show that a common model does not contain every provider field or
operation.

#### Apideck

Apideck exposes Unified APIs and a Proxy API. The Proxy API is used when a
provider field, endpoint, or operation is not available through the unified
resource. The caller then uses the provider's native API format.

#### Nango

Nango uses a code-first model in which developers define common operations and
implement provider-specific functions behind them. It supplies integration
infrastructure, authorization, execution, and observability, but developers
still own the provider mapping and behavior.

#### Paragon

Paragon provides embedded integrations, workflows, custom integrations, field
mapping, and a Proxy API. Its proxy handles access to a connected account while
the request still follows the provider's native API.

#### Unified API Finding

The unified API market demonstrates that the proposed architecture is viable
inside a defined business domain. It also demonstrates that provider-specific
logic cannot be eliminated. Mature products use a combination of:

- Common models
- Provider connectors
- Custom field mapping
- Access to raw provider data
- Provider-specific functions
- Proxy or passthrough requests

A passthrough endpoint is an escape hatch that sends an authenticated request
to the underlying provider using its native format. It is useful for advanced
functionality outside the canonical model but should not become the normal
integration path.

Sources:

- [Merge Field Mapping](https://docs.merge.dev/merge-unified/supplemental-data/field-mapping/overview)
- [Merge Remote Data](https://docs.merge.dev/merge-unified/supplemental-data/remote-data)
- [Merge Authenticated Passthrough Requests](https://docs.merge.dev/merge-unified/supplemental-data/passthrough-request/overview)
- [Apideck Proxy API](https://developers.apideck.com/guides/proxy-api-guide)
- [Nango Unified APIs](https://nango.dev/docs/getting-started/use-cases/unified-apis)
- [Paragon Proxy API](https://docs.useparagon.com/apis/proxy)

### 3. Generating MCP Servers from OpenAPI

OpenAPI describes the mechanical structure of an HTTP API, including paths,
methods, parameters, request bodies, response schemas, and authentication
schemes. This makes it useful for generating an initial MCP server or tool
surface.

Tools such as FastMCP and commercial generators can reduce boilerplate by
turning OpenAPI operations into tools. Generation can help with:

- Tool names and descriptions
- Input schemas
- HTTP method and path selection
- Basic request serialization
- Basic response typing

Automatic generation does not solve the semantic integration problem. An
OpenAPI document does not reliably explain:

- Which fields from two providers have the same business meaning
- Which provider statuses should map to one canonical status
- Whether an accepted request means completed, queued, or pending
- Which errors are retryable
- How idempotency should work
- Which provider capabilities are equivalent
- How asynchronous callbacks should be normalized
- Which fields are legally or operationally required

A human would not want to ship a raw generated server unchanged when it
contains hundreds of low-level endpoints, unclear tool descriptions,
provider-native errors, or unsafe write operations.

**Finding:** OpenAPI generation can accelerate the transport layer and create
an initial adapter skeleton. It cannot generate a complete, trustworthy
canonical integration without human design, review, and testing.

### 4. Traditional Integration Patterns

The proposed layer is a modern application of established integration
patterns.

#### Adapter Pattern

Each provider adapter converts the canonical interface into the provider's
incompatible interface and converts the provider response back into the
canonical model.

#### Anti-Corruption Layer

The canonical model prevents provider-specific terminology and behavior from
leaking throughout the client application. Provider changes are contained
inside their adapters.

#### Enterprise Service Bus and Integration Platforms

Platforms such as Apache Camel and MuleSoft provide routing, transformation,
connectors, retries, monitoring, and orchestration. They reduce repeated
infrastructure work, but they still require provider mappings and operational
configuration.

#### Part 1 Conclusion

Research supports the initial prediction. A common layer is practical when it
has a deliberately designed domain model and curated tool surface. It still
requires one reviewed adapter per provider, provider-specific workflow and
error handling, security controls, tests, and maintenance.

---

## Part 2 — Working Spike

**Status:** Completed.

### Objective and Scope

The spike tested whether one canonical MCP tool could route the same business
operation to three providers with different API structures.

The selected operation was sending an SMS. The providers were:

- Twilio
- Vonage
- MessageBird

The spike used simulation rather than live provider credentials because the
main question was whether canonical modelling, translation, routing, and MCP
invocation could work across different providers.

### Implemented Components

The implementation includes:

- Canonical `SMSRequest`, `SMSResponse`, and `SMSError` schemas
- Twilio, Vonage, and MessageBird adapters
- One shared MCP tool named `send_sms`
- A discovery tool named `get_requirements`
- Automated adapter and routing tests
- An MCP stdio smoke test

Each adapter performs two transformations:

```text
Canonical request -> Provider-specific request
Provider response -> Canonical response
```

The common request contains the provider, recipient, sender, message, and an
optional client reference. Changing the provider selects a different adapter
without changing the core operation.

### Executed Behavior

The following behavior was executed locally:

- Canonical request validation
- Invalid telephone-number rejection
- Request translation for all three providers
- Response translation for all three providers
- Provider routing through `send_sms`
- Status and error normalization
- Structured validation errors
- MCP server startup over stdio
- MCP client connection and tool discovery
- MCP tool invocation and canonical response retrieval

Tests were executed with:

```powershell
python -m pytest -v
```

The end-to-end smoke test was executed with:

```powershell
python scripts\smoke_test.py
```

The smoke test discovered `send_sms`, invoked it with the Twilio provider, and
received a successful simulated canonical response. The saved evidence is in
`docs/smoke_test_output.txt`.

### Provider Differences Observed

| Canonical concept | Twilio | Vonage | MessageBird |
|---|---|---|---|
| Recipient | `To` | `to` | `recipients` |
| Sender | `From` | `from` | `originator` |
| Message | `Body` | `text` | `body` |
| Message ID | `sid` | `message-id` | `id` |

Twilio and Vonage use form-style request fields in the spike, while
MessageBird uses a JSON structure containing a recipient list. Vonage returns
a `messages` array even for one message. MessageBird nests recipient status
inside a recipients object. Vonage uses numeric status codes while the other
providers primarily use textual statuses.

Simple differences such as field names, endpoint addresses, and some status
mappings can be represented declaratively. Nested arrays, empty responses,
numeric error interpretation, retry decisions, and lifecycle differences
require custom code.

### Execution Boundary

No live SMS was sent. The spike did not test real provider authentication,
billing, rate limits, outages, regulatory restrictions, delivery callbacks,
or final handset delivery. Requests and responses were based on documented
structures and example payloads.

### Spike Finding

The spike demonstrated that one MCP tool can accept a canonical SMS request,
route it through three provider adapters, and return a normalized response.
It also demonstrated that onboarding is not automatic. Every provider requires
documentation review, field mapping, authentication configuration,
translation logic, tests, and maintenance.

---

## Part 3 — Where the Universal Layer Breaks

### Evidence Basis

This section combines findings from the implemented SMS spike, executed tests,
MCP smoke test, provider documentation, and unified API research. The spike did
not test live authentication, real webhooks, billing, rate limits, or provider
outages.

### 1. Required Fields Needed by Only One Provider

One provider may require a campaign identifier, registered sender, agent
number, consent identifier, risk classification, or document reference that
other providers do not require.

The canonical schema can make some fields optional, but including every
provider-specific field would make it large and confusing. The recommended
solution has three levels:

1. Common canonical fields
2. Provider requirement and capability discovery
3. Controlled provider-specific extensions

The selected adapter must validate its additional requirements before making
the provider call. A few simple provider-only fields may add approximately
**1–3 hours** to onboarding; conditional rules can require considerably more.

**Finding:** Provider-only fields can be supported, but they cannot always be
hidden from the model or calling application.

### 2. Fields with the Same Name but Different Meanings

A field such as `status` may mean accepted, queued, sent to a carrier,
delivered, rejected, or completed depending on the provider. Direct field-name
mapping would create false equivalence.

The canonical model needs precisely defined statuses and must retain the
original provider status for diagnostics. Every provider status requires a
reviewed mapping and tests. Status mapping may add approximately **1–3 hours
per provider**, with more work for complex lifecycle models.

**Finding:** Matching field names do not prove matching business meaning.

### 3. Different Authentication Methods

Providers may use API keys, Basic authentication, OAuth 2.0, signed requests,
mutual TLS, rotating tokens, certificates, or IP allowlists.

Authentication belongs in the provider adapter or credential subsystem, not
in the canonical business schema. Credentials must be stored securely and
resolved using provider and tenant context. OAuth refresh, certificate
rotation, and scoped access require production-grade lifecycle management.

Simple API-key authentication may add **2–4 hours**. OAuth, signed requests,
or mutual TLS can add **8–24 hours or more**.

**Finding:** Authentication can be hidden from the MCP caller, but not from the
integration implementation and operations team.

### 4. Synchronous Responses versus Asynchronous Workflows

One provider may return a final result immediately while another returns an
accepted or queued response followed by a webhook or polling result.

The canonical lifecycle should use explicit states such as `pending`,
`succeeded`, `failed`, and `unknown`. Asynchronous providers also require
correlation identifiers, webhook verification or polling, state persistence,
timeouts, and duplicate-event handling.

The SMS spike already showed that initial provider acceptance does not prove
final delivery. Adding a simple asynchronous workflow may require **8–16
hours**, while complex workflows require more.

**Finding:** The canonical operation can hide transport differences, but it
cannot pretend asynchronous work is immediately complete.

### 5. Different Error Formats and Retry Behavior

Providers return errors using different HTTP statuses, codes, messages,
response bodies, and retry headers. Some errors are safe to retry; others
require corrected input or human action.

The layer should normalize errors into a stable structure containing a code,
message, retryable flag, provider code, provider message, and details. It
should preserve the original provider information for troubleshooting.

Error normalization and retry classification may add **3–6 hours per
provider**.

**Finding:** Normalized errors are essential for reliable LLM behavior, but
retryability must be decided using provider knowledge rather than guessed from
an HTTP status alone.

### 6. Idempotency and Duplicate Model Calls

An LLM or client may repeat a write operation because of a timeout, retry, or
uncertain response. Repeating operations such as policy creation, payment, or
SMS sending can create real cost and harm.

The canonical request should support an idempotency or client-reference key.
The layer should store the result of completed requests and return the same
result for duplicates. Where providers offer native idempotency keys, adapters
should use them. Otherwise, the layer must implement its own deduplication.

Basic protection may add **4–8 hours**, with additional storage and operations
work in a distributed production system.

**Finding:** Idempotency is a platform responsibility and is especially
important when the caller is an LLM.

### 7. Provider API Drift

Provider APIs change over time. Fields may become required, statuses may be
added, authentication can change, endpoints may be deprecated, and behavior
may change without a clean schema difference.

The layer requires contract tests, scheduled health checks, changelog
monitoring, schema validation, alerts for unknown statuses and errors, recorded
API versions, and clear ownership of each adapter.

Initial drift protection may add **3–6 hours per provider**. A reasonable early
maintenance estimate is **1–4 hours per provider per month**, excluding major
breaking changes.

**Finding:** Adapters are maintained products, not one-time generated files.

### 8. Capability Gaps between Providers

Providers may not support the same features. In the spike, MessageBird's API
can represent multiple recipients while the canonical operation deliberately
supports one recipient. In insurance, providers may differ in coverage types,
policy amendments, international coverage, document upload, cancellation, or
payment plans.

Capability differences should be exposed through provider metadata. An
unsupported request must return a clear `UNSUPPORTED_CAPABILITY` error and
must never silently drop fields.

A basic capability matrix may add **2–4 hours per provider**. Conditional
capabilities require more rules and testing.

**Finding:** Supported by the canonical tool does not mean supported by every
provider.

### Canonical-Model Decision

A least-common-denominator model is simple and predictable but may remove
valuable features. A superset model preserves more features but becomes large,
conditional, and difficult for models to use correctly.

The recommended hybrid is:

1. A stable canonical core
2. Capability discovery
3. Optional provider-specific extensions
4. Explicit unsupported-capability errors
5. Controlled passthrough for exceptional cases

### Part 3 Conclusion

The eight failure cases do not make the layer impossible. They show that its
promise cannot be:

```text
Give us any API and receive a complete integration automatically.
```

A more accurate promise is:

```text
Give us a documented API and provider access. We will onboard it into a
domain-specific MCP layer using a reusable framework, explicit mappings,
provider-specific logic, and tests.
```

---

## Part 4 — LLM Consumption and Tool Discovery

The existing `mcp-probe-groq` project provides the LLM host required for this
part of the assessment. A new host is unnecessary because it already connects
a Groq-hosted model to an MCP server, discovers the available tools, sends
their schemas to the model, executes tool calls, and returns results to the
model.

### Tool Discovery

The MCP client discovers tools from the server rather than relying on a
hard-coded interface. The universal SMS server exposes:

- `get_requirements`
- `send_sms`

`get_requirements` provides provider-specific required fields, sender rules,
recipient format, lifecycle information, and capabilities. This lets the
`send_sms` schema remain stable while provider-specific guidance remains
available when needed.

### Recovery from Missing Information

The canonical layer returns structured validation errors rather than exposing
unstructured provider errors. A structured error includes a stable code,
human-readable message, validation details, and retryability information.

An LLM can use that response to correct information already available in the
conversation or ask the user for a missing value. It should not invent missing
business information.

### Shared Tool versus Provider-Specific Tools

One shared `send_sms` tool is preferable for genuinely common SMS behavior. It
gives the model a smaller and more stable tool surface, while the validated
`provider` argument selects the correct adapter.

Separate provider tools are appropriate only when a provider exposes an
important operation that cannot be represented safely by the canonical model.
Provider-specific extensions or dedicated tools should handle those cases
instead of making the common schema excessively large.

### Part 4 Finding

An LLM can consume the universal layer through normal MCP discovery and tool
invocation. MCP solves exposure and discovery, but it does not eliminate
provider differences.

Reliable model behavior depends on clear tool descriptions, strict schemas,
requirement discovery, structured errors, capability metadata, idempotency,
and a limited tool surface.

---

## Cost and Onboarding Estimate

The initial **24–40 hour** estimate remains reasonable for onboarding a
moderately complex provider with usable documentation.

| Activity | Typical effort |
|---|---:|
| API documentation and workflow review | 4–6 hours |
| Canonical field and status mapping | 4–6 hours |
| Authentication and configuration | 2–6 hours |
| Adapter implementation | 6–10 hours |
| Error and retry normalization | 3–5 hours |
| Tests and fixtures | 4–6 hours |
| Documentation and review | 1–3 hours |
| **Estimated total** | **24–42 hours** |

The estimate is close to the initial 24–40 hour prediction; the upper bound is
rounded by the range of individual activities. Complex OAuth, certificates,
webhooks, regulatory rules, poor documentation, or large capability gaps can
increase the total substantially.

Reusable schemas, adapter templates, authentication components, test helpers,
and discovery conventions should reduce later onboarding effort, but they will
not remove provider analysis and validation.

Ongoing maintenance should be budgeted separately. A starting allowance of
**1–4 hours per provider per month** is reasonable, with additional effort for
breaking changes or incidents.

---

## Final Recommendation

Proceed with the universal MCP layer as a **domain-specific, adapter-based
platform**, not as a fully automatic integration generator.

The layer should promise a stable common interface for a defined business
operation. It should not promise that an arbitrary provider API can be
integrated without analysis, mapping, provider-specific code, testing, and
maintenance.

The recommended production architecture is:

1. A stable canonical core for common operations
2. One reviewed adapter for each provider
3. Provider requirement and capability discovery
4. Structured validation and provider errors
5. Idempotency protection for write operations
6. Support for asynchronous workflows
7. Optional provider-specific extensions
8. Controlled passthrough for exceptional functionality
9. Contract and regression testing for provider drift
10. Monitoring and clear ownership of every adapter

The assessment confirms the initial prediction: the concept is **viable under
specific conditions**. The original estimate of **24–40 working hours per
additional provider** remains a reasonable planning baseline, but it should be
increased for providers with complex authentication, asynchronous processes,
regulatory requirements, poor documentation, or major capability differences.
