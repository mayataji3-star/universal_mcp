"""Run the three Part 4 LLM experiments against the Universal SMS MCP server."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
API_KEY = os.getenv("GROQ_API_KEY")


def heading(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def serialize_result(result: Any) -> str:
    """Convert an MCP result into JSON text for the LLM and evidence file."""

    if hasattr(result, "model_dump"):
        value = result.model_dump(mode="json")
    else:
        value = str(result)

    return json.dumps(value, indent=2, ensure_ascii=False)


def mcp_tools_for_groq(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    """Convert MCP tool definitions into Groq function-tool definitions."""

    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        }
        for tool in mcp_tools
    ]


def assistant_message(message: Any) -> dict[str, Any]:
    """Convert a Groq assistant response into conversation history."""

    result: dict[str, Any] = {
        "role": "assistant",
        "content": message.content or "",
    }

    if message.tool_calls:
        result["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in message.tool_calls
        ]

    return result


async def run_agent(
    client: AsyncGroq,
    session: ClientSession,
    prompt: str,
    groq_tools: list[dict[str, Any]],
    maximum_rounds: int = 6,
) -> tuple[list[str], str]:
    """Allow the LLM to select and call MCP tools."""

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are testing an MCP server. Use the available tools when "
                "needed. Do not invent missing user information. If provider "
                "requirements are uncertain, use the discovery tool. Remember "
                "that this server operates in simulation mode."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    tool_sequence: list[str] = []

    for _ in range(maximum_rounds):
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            temperature=0,
        )

        message = response.choices[0].message
        messages.append(assistant_message(message))

        if not message.tool_calls:
            return tool_sequence, message.content or ""

        for call in message.tool_calls:
            name = call.function.name
            arguments = json.loads(call.function.arguments or "{}")
            tool_sequence.append(name)

            print(f"\nTool call: {name}")
            print("Arguments:")
            print(json.dumps(arguments, indent=2))

            result = await session.call_tool(name, arguments=arguments)
            result_text = serialize_result(result)

            print("Tool result:")
            print(result_text)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result_text,
                }
            )

    return tool_sequence, "Maximum number of tool rounds reached."


async def experiment_1(
    client: AsyncGroq,
    session: ClientSession,
    groq_tools: list[dict[str, Any]],
) -> None:
    """Test whether the model discovers requirements before sending."""

    heading("EXPERIMENT 1: CAPABILITY DISCOVERY")

    prompt = (
        "Prepare an SMS using MessageBird to +962790000000 from Example "
        "saying: Your appointment is tomorrow at 10 AM. Check any relevant "
        "provider requirements and use the available tools."
    )

    print("Prompt:")
    print(prompt)

    sequence, final_response = await run_agent(
        client,
        session,
        prompt,
        groq_tools,
    )

    passed = (
        "get_requirements" in sequence
        and "send_sms" in sequence
        and sequence.index("get_requirements") < sequence.index("send_sms")
    )

    print("\nObserved tool sequence:")
    print(sequence)
    print("\nFinal LLM response:")
    print(final_response)
    print("\nResult:", "PASS" if passed else "FAIL")
    print(
        "Interpretation:",
        "The model used discovery before the shared action."
        if passed
        else "The model did not use discovery before the shared action.",
    )


async def experiment_2(
    client: AsyncGroq,
    session: ClientSession,
) -> None:
    """Test LLM recovery after receiving a structured validation error."""

    heading("EXPERIMENT 2: RECOVERY FROM A MISSING FIELD")

    bad_arguments = {
        "provider": "twilio",
        "to": "+962790000000",
        "sender": "",
        "message": "Your appointment is tomorrow at 10 AM.",
    }

    print("Simulated first tool call:")
    print(json.dumps(bad_arguments, indent=2))

    error_result = await session.call_tool(
        "send_sms",
        arguments=bad_arguments,
    )
    error_text = serialize_result(error_result)

    print("\nStructured tool result:")
    print(error_text)

    messages = [
        {
            "role": "system",
            "content": (
                "You are evaluating recovery from MCP tool errors. "
                "Do not invent missing information. Explain what is missing "
                "and what must happen before retrying."
            ),
        },
        {
            "role": "user",
            "content": (
                "Send an SMS through Twilio to +962790000000 saying: "
                "Your appointment is tomorrow at 10 AM. "
                "I did not provide a sender."
            ),
        },
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "recovery_test_call",
                    "type": "function",
                    "function": {
                        "name": "send_sms",
                        "arguments": json.dumps(bad_arguments),
                    },
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "recovery_test_call",
            "content": error_text,
        },
    ]

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )

    final_response = response.choices[0].message.content or ""
    response_lower = final_response.lower()

    passed = (
        "sender" in response_lower
        and (
            "provide" in response_lower
            or "missing" in response_lower
            or "required" in response_lower
        )
    )

    print("\nFinal LLM response:")
    print(final_response)
    print("\nResult:", "PASS" if passed else "FAIL")
    print(
        "Interpretation:",
        "The model recognized the missing sender and did not invent it."
        if passed
        else "The model did not clearly recover from the missing sender.",
    )


def separate_provider_tools() -> list[dict[str, Any]]:
    """Return three provider-specific tool definitions for comparison."""

    tools = []

    descriptions = {
        "send_twilio_sms": "Prepare an SMS using Twilio.",
        "send_vonage_sms": "Prepare an SMS using Vonage.",
        "send_messagebird_sms": "Prepare an SMS using MessageBird.",
    }

    for name, description in descriptions.items():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient in international format.",
                            },
                            "sender": {
                                "type": "string",
                                "description": "SMS sender.",
                            },
                            "message": {
                                "type": "string",
                                "description": "SMS message text.",
                            },
                        },
                        "required": ["to", "sender", "message"],
                        "additionalProperties": False,
                    },
                },
            }
        )

    return tools


async def choose_tool(
    client: AsyncGroq,
    prompt: str,
    tools: list[dict[str, Any]],
) -> str:
    """Ask the model to select one tool and return its name."""

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Select the correct SMS tool for the user's request.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        tools=tools,
        tool_choice="required",
        temperature=0,
    )

    calls = response.choices[0].message.tool_calls or []

    if not calls:
        return "NO_TOOL_SELECTED"

    return calls[0].function.name


async def experiment_3(
    client: AsyncGroq,
    universal_send_tool: dict[str, Any],
) -> None:
    """Compare one shared tool with three provider-specific tools."""

    heading("EXPERIMENT 3: SHARED TOOL VERSUS SEPARATE TOOLS")

    prompts = [
        (
            "Using Twilio, send +962790000000 a message from Example "
            "saying Test one."
        ),
        (
            "Using Vonage, send +962790000000 a message from Example "
            "saying Test two."
        ),
        (
            "Using MessageBird, send +962790000000 a message from Example "
            "saying Test three."
        ),
    ]

    expected_separate = [
        "send_twilio_sms",
        "send_vonage_sms",
        "send_messagebird_sms",
    ]

    shared_correct = 0
    separate_correct = 0

    for index, prompt in enumerate(prompts):
        shared_choice = await choose_tool(
            client,
            prompt,
            [universal_send_tool],
        )
        separate_choice = await choose_tool(
            client,
            prompt,
            separate_provider_tools(),
        )

        if shared_choice == "send_sms":
            shared_correct += 1

        if separate_choice == expected_separate[index]:
            separate_correct += 1

        print(f"\nPrompt {index + 1}: {prompt}")
        print("Shared-tool choice:", shared_choice)
        print("Separate-tool choice:", separate_choice)
        print("Expected separate tool:", expected_separate[index])

    print(f"\nShared-tool correct selections: {shared_correct}/3")
    print(f"Separate-tool correct selections: {separate_correct}/3")

    passed = shared_correct == 3 and separate_correct == 3

    print("Result:", "PASS" if passed else "REVIEW REQUIRED")
    print(
        "Interpretation: Both designs can work for explicit provider names. "
        "The shared tool provides a smaller and more stable MCP surface, "
        "while separate tools can expose provider-specific capabilities."
    )


async def main() -> None:
    if not API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to the private .env file."
        )

    client = AsyncGroq(api_key=API_KEY)

    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.server"],
        cwd=str(ROOT),
    )

    async with stdio_client(server_parameters) as streams:
        read_stream, write_stream = streams

        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            listed_tools = await session.list_tools()
            groq_tools = mcp_tools_for_groq(listed_tools.tools)

            print("Model:", MODEL)
            print("Discovered MCP tools:")
            print([tool.name for tool in listed_tools.tools])

            await experiment_1(
                client,
                session,
                groq_tools,
            )

            await experiment_2(
                client,
                session,
            )

            universal_send_tool = next(
                tool
                for tool in groq_tools
                if tool["function"]["name"] == "send_sms"
            )

            await experiment_3(
                client,
                universal_send_tool,
            )


if __name__ == "__main__":
    asyncio.run(main())