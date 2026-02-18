import config
import requests

def register_get_api_docs(mcp):

    @mcp.tool(name="api_documentation", title="API Documentation")
    def get_api_docs():
        """
        Retrieve the full urlDNA OpenAPI specification (v3) from the official documentation repository.

        Use this tool whenever a user asks:
        - How to use the urlDNA API
        - What endpoints are available
        - What parameters or request/response schemas are expected
        - How authentication works
        - What HTTP methods or status codes are used
        - How to integrate or call the urlDNA API directly

        This tool fetches the live OpenAPI JSON spec from:
            https://github.com/urldna/docs/blob/main/api-reference/openapi.json

        The spec includes:
            - All available API endpoints (paths)
            - HTTP methods (GET, POST, etc.)
            - Request body schemas and required fields
            - Response schemas and status codes
            - Authentication requirements
            - Data models and object definitions

        No arguments are required.

        Returns:
            dict: The full urlDNA OpenAPI 3.x specification as a parsed JSON object.
        Raises:
            RuntimeError: If the OpenAPI spec cannot be fetched from GitHub.
        """
        try:
            res = requests.get(config.OPENAPI_URL, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"[get_api_docs] Failed to fetch OpenAPI spec: {e}")

        try:
            return res.json()
        except ValueError as e:
            raise RuntimeError(f"[get_api_docs] Failed to parse OpenAPI spec as JSON: {e}")