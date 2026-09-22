# Part 4 Experiment Predictions

These predictions were recorded before running the experiments.

## Experiment 1: Capability discovery

I predict that the LLM will call `get_requirements` before calling
`send_sms` when it is unsure about a provider's requirements.

The discovery tool should improve reliability because it gives the model
provider-specific rules without making the universal tool schema excessively
large.

## Experiment 2: Recovery from invalid or missing information

I predict that the LLM will understand a structured validation error and
either correct the request using information already available or ask the
user for the missing value.

Structured errors should work better than unstructured provider error
messages.

## Experiment 3: Shared tool versus separate tools

I predict that one shared `send_sms` tool will be easier to discover and use
for equivalent SMS operations.

Separate provider-specific tools may be useful when providers have important
capabilities that cannot be represented safely by the shared canonical model.