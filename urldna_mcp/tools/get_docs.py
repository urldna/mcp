import json
import requests
import config
import uuid

def register_docs_search(mcp):

    @mcp.tool(name="search_docs")
    def search_docs(query: str):
        """
        Search the official urlDNA documentation for integrations, API usage, and guides.
        
        Args:
            query (str): The search term (e.g., 'Slack integration', 'API rate limits').
        """
        
        # Mintlify requires these specific headers to initiate the SSE stream
        headers = {
            "Accept": "text/event-stream, application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "jsonrpc": "2.0",
            "id": f"urlDNA-search-{uuid.uuid4()}",
            "method": "tools/call",
            "params": {
                "name": "SearchUrlDnaDocumentation",
                "arguments": {"query": query}
            }
        }

        try:
            # We use stream=True because the server returns text/event-stream
            response = requests.post(config.MCP_DOC_URL, headers=headers, json=payload, stream=True, timeout=15)
            response.raise_for_status()

            # SSE responses come in blocks starting with "data: "
            full_content = []
            for line in response.iter_lines():
                if not line:
                    continue
                
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:] # Strip "data: "
                    try:
                        data_json = json.loads(data_str)
                        
                        # Mintlify usually nests the answer in result -> content
                        if "result" in data_json and "content" in data_json["result"]:
                            # Extracting the actual text content from the MCP tool output
                            for item in data_json["result"]["content"]:
                                if item.get("type") == "text":
                                    full_content.append(item.get("text"))
                    except json.JSONDecodeError:
                        continue

            return "\n".join(full_content) if full_content else "No documentation found for that query."

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Documentation search failed: {str(e)}")