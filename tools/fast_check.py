import requests
import config
from utils import get_api_key


def register_fast_check(mcp):

    @mcp.tool()
    def fast_check(url: str):
        """
        Fast check if a URL has already been scanned.

        Args:
            url (str): URL to be verified.
        Returns:
            dict: Fast check result JSON.
        Raises:
            RuntimeError: If check fails.
        """
        # Get urlDNA API key 
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[new_scan] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.post(f"{config.urlDNA_API_URL}/fast-check", json={"url": url}, headers=headers)

        if not res.ok:
            raise RuntimeError(f"[fast_check] Request failed: {res.status_code} - {res.text}")

        return res.json()
