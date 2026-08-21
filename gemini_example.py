import asyncio

import httpx
from google import genai
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Initialize Gemini client (assumes GEMINI_API_KEY is set via environment variable)
client = genai.Client()

MCP_SERVER_URL = "https://mcp.urldna.io/"
MCP_HEADERS = {
    "x-api-key": "<URLDNA_API_KEY>"  # Replace with your urlDNA API key
}


async def main():
    async with httpx.AsyncClient(headers=MCP_HEADERS) as http_client:
        async with streamable_http_client(MCP_SERVER_URL, http_client=http_client) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()

                response = await client.aio.models.generate_content(
                    model="gemini-3.5-flash",
                    contents="Search in urlDNA for malicious scans with title like paypal",
                    config=genai.types.GenerateContentConfig(
                        system_instruction="You are a cybersecurity analyst using urlDNA.",
                        temperature=0.7,
                        # Gemini automatically discovers and calls the tools exposed
                        # by the MCP session (fast_check, new_scan, get_scan, search,
                        # saved queries, brand monitoring, search_docs, ...).
                        tools=[session],
                    ),
                )

                print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
