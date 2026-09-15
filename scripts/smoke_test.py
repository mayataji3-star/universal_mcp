"""Launch the MCP server and call send_sms through an MCP client."""

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.server"],
    )

    async with stdio_client(server_parameters) as streams:
        read_stream, write_stream = streams

        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]

            print("Discovered MCP tools:")
            print(json.dumps(tool_names, indent=2))

            if "send_sms" not in tool_names:
                raise RuntimeError("send_sms was not discovered")

            result = await session.call_tool(
                "send_sms",
                arguments={
                    "provider": "twilio",
                    "to": "+962790000000",
                    "sender": "Example",
                    "message": "Hello through MCP",
                    "client_reference": "smoke-test-001",
                },
            )

            print("\nMCP tool result:")

            for content in result.content:
                text = getattr(content, "text", None)

                if text is not None:
                    print(text)
                else:
                    print(content)

            if result.isError:
                raise RuntimeError("The MCP tool returned an error")

            print("\nMCP smoke test passed.")


if __name__ == "__main__":
    asyncio.run(main())