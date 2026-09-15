# Universal MCP Layer Viability Assessment

## Executive Summary

**Status:** To be completed after the research and working spike.

The final executive summary will state whether the proposed universal MCP layer
is viable, viable under specific conditions, or not viable. It will also provide
a rough estimate of the effort required to onboard an additional company.

## Initial Prediction

The prediction made before starting the research and implementation is preserved
unchanged in [INITIAL_PREDICTION.md](INITIAL_PREDICTION.md).

The initial prediction was that the system would be **viable under specific
conditions**, with an estimated onboarding cost of **24–40 working hours per
additional company**.

---

## Part 1 — Existing Solutions and Architecture

### Research Method

This part is based on documentation research. No vendor platform or ACORD
integration was executed during this phase.

The working spike and executed experiments will be documented separately from
the research findings.

---

### 1. Domain Standards

#### ACORD Insurance Standards

##### What I researched

I reviewed ACORD's official descriptions of its insurance data standards and
Reference Architecture. The purpose was to determine whether insurance already
has a common model that could be used by the universal MCP layer.

This section is based on documentation research only. I have not implemented or
executed an ACORD integration.

##### What ACORD provides

ACORD is an insurance industry standards organization. It provides data
standards for several insurance sectors, including Property and Casualty, Life
and Annuity, and Global Reinsurance and Large Commercial insurance.

For Property and Casualty insurance, ACORD provides AL3 and XML standards. AL3
is intended for one-way batch communication of policy and commission data,
while the XML standards support real-time request-and-response transactions.

ACORD also provides Next-Generation Digital Standards. These are granular,
transaction-focused standards intended for modern interfaces such as REST APIs
and microservices.

Sources:

* [ACORD Data Standards](https://www.acord.org/standards-architecture/acord-data-standards)
* [ACORD Property and Casualty Data Standards](https://www.acord.org/standards-architecture/acord-data-standards/Property_Casualty_Data_Standards)
* [ACORD Next-Generation Digital Standards announcement](https://www.acord.org/ACORD-about/acord-news/2020/04/08/acord-releases-next-generation-digital-standards-to-enable-streamlined-insurance-data-exchange)

##### Does ACORD provide a canonical insurance model?

Yes. ACORD provides an important starting point for a canonical insurance
model. Its Reference Architecture includes business processes, product models,
an Information Model, a Data Model, and a Capability Model.

The Information Model organizes insurance concepts and their relationships.
The Data Model provides a logical structure generated from that Information
Model. Therefore, the proposed MCP layer should evaluate ACORD before inventing
a completely new policy model.

However, ACORD is broader than the schema of a single `create_policy` tool. The
project would still need to select the relevant ACORD concepts and define a
smaller operational request and response contract for that tool.

Sources:

* [ACORD Reference Architecture](https://www.acord.org/standards-architecture/reference-architecture)
* [ACORD Framework Overview](https://www.acord.org/staticfiles/reference_architecture/overview/story_html5.html)

##### Does ACORD eliminate provider adapters?

No. ACORD provides common insurance concepts and exchange standards, but it
does not guarantee that every insurance company's existing API follows the
same standard, version, workflow, or interpretation.

Each company would still require an adapter that maps:

1. The MCP canonical request to the company's API request.
2. The company's API response to the MCP canonical response.
3. The company's authentication, errors, lifecycle, and unsupported
   capabilities.

Even when two companies claim ACORD compatibility, implementation testing would
still be necessary because they may support different subsets or versions of
the standards.

##### Access and licensing consideration

Some ACORD materials are publicly described, but important standards packages
and detailed implementation resources may require access through an ACORD
Standards program or membership.

For example, ACORD states that its Next-Generation Digital Standards are
available for download by members of its Standards programs.

Before using ACORD in a commercial universal layer, the team would therefore
need to confirm the applicable access, membership, and licensing terms.

Source:

* [ACORD Next-Generation Digital Standards announcement](https://www.acord.org/ACORD-about/acord-news/2020/04/08/acord-releases-next-generation-digital-standards-to-enable-streamlined-insurance-data-exchange)

##### Finding and design impact

**Finding:** Insurance already has industry data models and messaging standards,
so the project should not invent its insurance vocabulary entirely from
scratch.

**Design impact:** ACORD can provide the semantic foundation for the canonical
model, but it cannot provide automatic compatibility with every company's API.
The universal MCP layer still requires a tested adapter for each provider.

**Preliminary conclusion:** ACORD makes the universal MCP layer more viable, but
it does not make onboarding a new insurance company automatic.

---

### 2. Unified API Platforms

#### What I researched

I reviewed the official documentation for Merge, Apideck, Nango, and Paragon
to understand how existing integration platforms connect one interface to many
different provider APIs.

This section is based on documentation research only. I have not installed,
executed, or tested these platforms.

#### Standard architecture

The platforms use the same general architecture proposed for the universal MCP
layer:

1. The client sends a request using a common model.
2. The platform chooses the correct provider integration.
3. Provider-specific logic translates the common request into the provider's
   request format.
4. The provider API is called using the appropriate authentication.
5. The result is translated back into a common response.

This reduces work for the client, but it does not remove provider-specific
integration work from the platform.

#### Merge

Merge exposes Common Models that normalize concepts across multiple providers.
However, not all provider fields fit inside these models.

Merge provides several escape mechanisms:

* **Remote Data** exposes data in the provider's original format.
* **Field Mapping** maps provider-specific and custom fields into new fields on
  a Common Model.
* **Remote Field Classes** expose fields that are not mapped to the Common
  Model.
* **Authenticated Passthrough Requests** call the underlying provider API
  directly when the required data or operation is not covered by a Common
  Model.

Merge's passthrough documentation states that passthrough requests use the
specific format of the underlying provider rather than Merge's unified format.
Merge therefore handles authentication and routing, but the customer must
understand that provider's native API.

Sources:

* [Merge Field Mapping](https://docs.merge.dev/merge-unified/supplemental-data/field-mapping/overview)
* [Merge Remote Data](https://docs.merge.dev/merge-unified/supplemental-data/remote-data)
* [Merge Remote Field Classes](https://docs.merge.dev/merge-unified/supplemental-data/remote-field-classes/remote-field-classes)
* [Merge Authenticated Passthrough Requests](https://docs.merge.dev/merge-unified/supplemental-data/passthrough-request/overview)

#### Apideck

Apideck provides Unified APIs that map different providers in the same category
to common resources and operations.

Apideck also provides a Proxy API. Its documentation explains that this API can
call a connector-native endpoint when the unified resource does not expose the
required field, endpoint, or operation.

Therefore, Apideck's common API does not cover every provider capability. When
a feature falls outside the unified model, the caller uses the provider's
native request format through the proxy.

Sources:

* [Apideck API Integrations](https://www.apideck.com/api-integrations)
* [Apideck Proxy API guide](https://developers.apideck.com/guides/proxy-api-guide)
* [Apideck Unified Pass Through](https://developers.apideck.com/guides/pass-through)

#### Nango

Nango uses a code-first approach. The developer defines the common model and
operations required by the product. A provider-specific function is then
implemented for each external API to translate data to and from that model.

Nango therefore provides infrastructure and reusable integration tooling, but
it does not claim that one schema can be generated automatically for every
provider. Its official documentation explicitly describes provider-specific
functions behind a stable interface.

Nango also handles shared integration concerns such as authorization,
execution, and observability. Nevertheless, developers still own the mapping
and provider-specific behavior.

Sources:

* [Nango: Build a unified API](https://nango.dev/docs/getting-started/use-cases/unified-apis)
* [Nango Unified APIs with functions](https://nango.dev/docs/guides/functions/unified-apis)
* [Introduction to Nango](https://nango.dev/docs/getting-started/intro-to-nango)

#### Paragon

Paragon is closer to an embedded integration platform than a fixed unified data
model. It provides prebuilt integrations, workflows, an SDK, and a Proxy API.

Paragon's Proxy API allows an application to call any method of a connected
third-party provider. Paragon manages access to the connected account, but the
request still follows the provider's native API.

Paragon also supports custom integrations and custom field mapping. This
indicates that prebuilt actions cannot cover every provider or customer
requirement.

Sources:

* [Paragon Proxy API](https://docs.useparagon.com/apis/proxy)
* [Paragon Custom Integrations](https://docs.useparagon.com/resources/custom-integrations)
* [Paragon Custom Field Mapping](https://docs.useparagon.com/workflows/advanced-techniques/implementing-custom-field-mapping)

#### Are provider adapters generated automatically?

The evidence does not support the claim that these platforms can automatically
create a complete production integration from any arbitrary API.

Nango states most clearly that provider-specific functions translate between
each provider API and the common model. Merge and Apideck expose predefined
connectors and common models, but their field-mapping and passthrough features
demonstrate that provider differences still require explicit handling.

Code generation or AI may accelerate the first implementation, but a human must
still decide:

* Which provider fields correspond to the common model
* How required provider-only fields are supplied
* How values and status codes are translated
* Which errors can be retried
* How authentication and permissions are configured
* How asynchronous operations and webhooks behave
* Which provider capabilities are unsupported
* How the adapter is tested and maintained

#### How are provider-only fields handled?

Existing platforms use a combination of:

1. Common fields for functionality shared across providers.
2. Custom or remote field mapping.
3. Access to raw provider data.
4. Provider-specific functions.
5. Passthrough or proxy calls for unsupported operations.

This is more practical than forcing every provider feature into one universal
schema.

#### What is a passthrough endpoint?

A passthrough endpoint sends an authenticated request through the integration
platform to the underlying provider's native API.

It is needed when the common API does not support a provider-specific field,
endpoint, or operation. The platform can still supply authentication and
routing, but the caller must use the provider's own URL, parameters, payload,
and response format.

Passthrough is therefore an escape hatch from the common model.

#### Main finding

The unified API market proves that a common integration layer is viable within
a defined business domain. However, these products do not eliminate
provider-specific work.

They move that work into maintained connectors, mapping rules, custom fields,
provider functions, and passthrough endpoints.

The fact that mature platforms provide passthrough access is evidence that no
single canonical model preserves every feature of every provider.

#### Design implication for the universal MCP layer

The proposed MCP layer should copy this hybrid design:

* A canonical model for common operations
* One tested adapter per provider
* Capability discovery for provider differences
* Optional provider-specific extension fields
* A controlled passthrough mechanism for unsupported advanced functionality

The system is therefore not “bring any API and automatically receive a complete
MCP integration.” Each new company will still require analysis, mapping,
testing, and possibly custom code.

---

### 3. Generating MCP Servers from OpenAPI Specifications

#### What I researched

I reviewed documentation for OpenAPI, FastMCP, Speakeasy, Stainless, and
OpenAPI-to-MCP server projects.

This section is based on documentation research only. I have not yet generated
or executed an MCP server from an OpenAPI specification.

#### What OpenAPI provides

OpenAPI is a standard, language-independent description of an HTTP API. An
OpenAPI document can describe:

* API endpoints and HTTP methods
* Request parameters
* Request and response schemas
* Authentication schemes
* Operation names and descriptions
* Expected response codes

Because this information resembles an MCP tool definition, an OpenAPI document
can be used to generate MCP tools automatically.

Source:

* [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification)

#### FastMCP OpenAPI support

FastMCP can create an MCP server from an existing OpenAPI specification using
`FastMCP.from_openapi()`.

By default, FastMCP converts every endpoint in the specification into an MCP
tool. Developers can customize the result using route mappings, including
rules that exclude internal or unsuitable endpoints.

FastMCP's documentation warns that generated servers are most useful for
bootstrapping and prototyping. It states that language models perform better
with curated MCP servers than with automatically converted APIs, particularly
when the API contains many endpoints and parameters.

Sources:

* [FastMCP OpenAPI integration](https://gofastmcp.com/integrations/openapi)
* [FastMCP and FastAPI integration](https://gofastmcp.com/integrations/fastapi)

#### Speakeasy

Speakeasy explains that an OpenAPI document contains enough structural
information to generate a functioning MCP server. Endpoint paths become tools,
request schemas become tool inputs, and response schemas describe the returned
data.

However, Speakeasy also identifies limits to automatic generation. The quality
of the generated tools depends heavily on the quality of the OpenAPI document.
Weak operation names, vague descriptions, missing examples, and unclear
parameter documentation produce tools that are difficult for a model to select
and use correctly.

Source:

* [Speakeasy: Generating MCP tools from OpenAPI](https://www.speakeasy.com/mcp/tool-design/generate-mcp-tools-from-openapi/)

#### Stainless

Stainless generates SDKs, documentation, and MCP servers from OpenAPI
specifications. It also provides configuration and transformation features for
correcting or customizing the source specification.

The existence of these transformations is significant. Automatic generation
can reproduce the structure described by an API specification, but teams may
still need to correct types, add missing required fields, rename properties,
exclude operations, and customize authentication or methods.

Sources:

* [Stainless](https://www.stainless.com/)
* [Stainless transforms](https://www.stainless.com/changelog/transforms/)
* [Stainless MCP resources](https://www.stainless.com/mcp/resources/)

#### Open-source OpenAPI-to-MCP servers

Open-source projects can dynamically expose OpenAPI operations as MCP tools.

For example, the AWS Labs OpenAPI MCP Server supports automatic tool
generation, route mapping, tag-based filtering, multiple specifications,
authentication configuration, and enriched tool descriptions.

These features show that conversion is technically straightforward, but they
also show that configuration and curation remain necessary. Teams must decide
which endpoints should be available to the model and which must be hidden.

Sources:

* [AWS Labs OpenAPI MCP Server](https://awslabs.github.io/mcp/servers/openapi-mcp-server)
* [OpenAPI MCP Server](https://github.com/ivo-toby/mcp-openapi-server)

#### How far does automatic generation get?

Automatic generation can provide:

1. A running MCP server scaffold.
2. One MCP tool for each selected API operation.
3. Input schemas based on API parameters and request bodies.
4. HTTP request forwarding.
5. Basic authentication forwarding.
6. Basic response handling.
7. A repeatable way to regenerate the server when the specification changes.

This is useful for prototypes and for APIs that are small, well documented,
consistent, and designed for external consumers.

#### What automatic generation does not solve

OpenAPI describes the technical contract of one API. It does not automatically
understand how one company's business concepts correspond to another company's
concepts.

Generation does not decide:

* Whether `customer_name` and `policy_holder` mean the same thing
* Which provider-only fields belong in the canonical model
* How to translate values, statuses, and error meanings
* Whether an operation is safe for autonomous model use
* How multiple API calls form one business workflow
* How asynchronous operations and webhooks should be represented
* Which errors should be retried
* How idempotency should work across providers
* How three different APIs should become one `create_policy` operation

Therefore, generating three MCP servers from three API specifications would
normally produce three sets of provider-native tools. It would not
automatically produce one correct canonical `create_policy` tool.

#### What a human would not want to ship unchanged

A direct conversion may expose every API endpoint as a tool, including
administrative, dangerous, irrelevant, or low-level operations.

It may also produce:

* Too many tools for reliable model selection
* Long or awkward tool names based on endpoint operation IDs
* Vague descriptions copied from weak API documentation
* Large and complicated parameter schemas
* Provider-native responses instead of a canonical response
* Technical errors that do not help the model recover
* Tools that expose sensitive operations without adequate controls
* Separate low-level calls where the user expects one business operation

A production implementation therefore requires tool selection, clearer
descriptions, access controls, error design, workflow design, tests, and
monitoring.

#### Main finding

OpenAPI-to-MCP generation is valuable scaffolding, but it is not an automatic
unification solution.

It can reduce the mechanical work required to expose one company's API through
MCP. It cannot remove the semantic and business work required to translate
several different company APIs into one reliable canonical tool.

#### Design implication

The universal layer can use OpenAPI generation to accelerate development of
provider clients or initial MCP tools. However, the production architecture
still requires:

* A deliberately designed canonical schema
* A curated MCP tool surface
* One reviewed adapter per provider
* Provider-specific workflow and error handling
* Security controls
* Contract and model-behavior tests

---

### 4. Traditional Integration Patterns

#### What I researched

I reviewed established software integration patterns and platforms to understand
how they relate to the proposed universal MCP layer.

This section is based on documentation research only. I have not implemented
Apache Camel or MuleSoft as part of the spike.

#### Adapter Pattern

The Adapter Pattern allows one interface to work with another system that has
an incompatible interface.

In this project, every provider adapter accepts the canonical request and
translates it into the provider's API format. It then translates the provider's
response back into the canonical response.

For example:

```text
Canonical SMS request
        |
        v
Twilio adapter
        |
        v
Twilio API requestThe research completed so far supports the initial prediction that a universal
MCP layer is viable only under specific conditions.

ACORD can provide a common insurance vocabulary and data-model foundation.
Existing unified API companies demonstrate that many providers can be placed
behind one interface. OpenAPI generation can also reduce the mechanical effort
required to expose an existing API through MCP.

However, none of these approaches completely eliminates provider-specific
integration work.

A realistic architecture requires:

1. A domain-specific canonical model.
2. One adapter per provider.
3. Provider capability metadata.
4. Custom or extension fields.
5. A passthrough mechanism for unsupported features.
6. Human review and testing.
7. Continuous monitoring for provider API changes.

The final conclusion will be made after building and testing the working spike.

---

## Part 2 — Working Spike

**Status:** Not yet started.

The spike will use three publicly documented APIs that perform the same action
using different request and response structures.

The selected API family, canonical schema, adapters, tests, and execution
results will be documented here.

This section will clearly separate:

* Functionality that was implemented and executed
* Transformations that were tested locally
* Behavior that was mapped from documentation only
* Calls that were not sent to live provider APIs

---

## Part 3 — Where the Universal Layer Breaks

**Status:** To be completed after the spike.

The assessment will provide a specific answer for each of the following issues.

### 1. Required fields needed by only one provider

To be completed.

### 2. Fields with the same name but different meanings

To be completed.

### 3. Different authentication methods

To be completed.

### 4. Synchronous responses versus asynchronous workflows

To be completed.

### 5. Different error formats and retry behavior

To be completed.

### 6. Idempotency and duplicate model calls

To be completed.

### 7. Provider API drift

To be completed.

### 8. Capability gaps between providers

To be completed.

### Canonical model trade-off

The final assessment will determine whether the common schema becomes:

* A least-common-denominator model that works everywhere but exposes only basic
  features
* A superset model containing many fields that are unsupported by some
  providers
* A hybrid model combining common fields, capability discovery, extensions,
  and passthrough access

---

## Part 4 — Does an AI Model Change the Integration Problem?

**Status:** Experiments not yet executed.

The experiments will test:

1. Whether a `get_requirements(provider)` discovery tool helps the model supply
   provider-specific fields.
2. Whether the model can recover from a structured missing-field error and
   retry correctly.
3. Whether one tool with a `provider` parameter performs better or worse than
   three provider-specific tools.

The actual prompts, tool calls, results, and failures will be preserved in the
repository.

---

## Cost Model

**Status:** Initial estimate only.

The initial estimate is **24–40 working hours** to onboard one additional
company. This estimate will be revised after completing the spike.

The final cost model will separately estimate:

* API documentation review
* Canonical field mapping
* Adapter implementation
* Authentication configuration
* Response normalization
* Error and retry mapping
* Webhook or asynchronous workflow handling
* Contract tests
* Model behavior tests
* Documentation
* Ongoing maintenance and drift monitoring

---

## Final Recommendation

**Status:** To be completed after the spike.**

The final recommendation will choose one of the following without ending in
“it depends”:

* Viable
* Viable under explicitly named conditions
* Not viable

The recommendation will include the required conditions and an estimated
onboarding cost for company number four.
