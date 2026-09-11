# test_client.py
import asyncio
from mcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        result = await client.call_tool("list_decks", {})
        print(result.content)

asyncio.run(main())