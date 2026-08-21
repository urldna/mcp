import os
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from google import genai

async def main():
    # 1. Connect FastMCP client directly to streamable-http
    transport = StreamableHttpTransport(
        "https://mcp.urldna.io/",
        headers={"x-api-key": os.getenv("URLDNA_API_KEY", "YOUR_KEY")},
    )
    client_mcp = Client(transport)
    
    async with client_mcp:
        ai = genai.Client(vertexai=True, project=os.getenv("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID"))
        response = await ai.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Search in urlDNA for malicious scans with title like paypal",
            config=genai.types.GenerateContentConfig(tools=[client_mcp.session]),
        )
        
        print(response.text)

if __name__ == "__main__":
    asyncio.run(main())