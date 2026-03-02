import json
import uuid
import httpx

import config


def register_docs_search(mcp):

    @mcp.tool(name="search_docs")
    async def search_docs(query: str):
        """
        Search the official urlDNA documentation for integrations, API usage, and guides.
        
        Args:
            query (str): The search term (e.g., 'Slack integration', 'API rate limits').
        """

        headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": f"urlDNA-search-{uuid.uuid4()}",
            "method": "tools/call",
            "params": {"name": "SearchUrlDnaDocumentation", "arguments": {"query": query}}
        }

        async with httpx.AsyncClient() as client:
            full_content = []
            # Use stream to handle the event-stream asynchronously
            async with client.stream("POST", config.MCP_DOC_URL, headers=headers, json=payload, timeout=20.0) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data_json = json.loads(line[6:])
                            if "result" in data_json and "content" in data_json["result"]:
                                for item in data_json["result"]["content"]:
                                    if item.get("type") == "text":
                                        full_content.append(item.get("text"))
                        except: continue
            
            return "\n".join(full_content) if full_content else "No documentation found."