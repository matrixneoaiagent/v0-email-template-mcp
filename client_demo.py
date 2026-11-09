#!/usr/bin/env python3
"""Call the SpendWarden email MCP server through FastMCP's stdio client."""
import asyncio
from fastmcp import Client

async def main() -> None:
    async with Client("server.py") as client:
        tools = await client.list_tools()
        print("TOOLS:", [t.name for t in tools])
        result = await client.call_tool(
            "send_email",
            {
                "to": "opencode.agent177c@onionmail.org",
                "subject": "SpendWarden email template demo",
                "html": "",
                "text": "",
            },
        )
        print("RESULT:")
        for item in result.content:
            print(getattr(item, "text", item))

if __name__ == "__main__":
    asyncio.run(main())
