import requests
import config
from utils import get_api_key, normalize_url


def register_fast_check(mcp):

    @mcp.tool()
    def fast_check(url: str):
        """
        Quickly check if a URL has already been scanned in the urlDNA database.

        This is a lightweight lookup — it does not submit a new scan. Use this
        to avoid redundant scans and get instant results if the URL was previously analyzed.

        The URL is automatically normalized: if no scheme is provided (e.g., "example.com"),
        "https://" is prepended automatically.

        Args:
            url (str): URL to check. Can be provided with or without the "https://" prefix.
                       Examples: "https://example.com", "example.com", "www.phishing-site.net"
        Returns:
            dict: Fast check result from urlDNA, including scan_id if a match is found.
        Raises:
            RuntimeError: If the API key retrieval or the HTTP request fails.
        """
        # Normalize URL
        url = normalize_url(url)

        # Get urlDNA API key
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[fast_check] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.post(f"{config.urlDNA_API_URL}/fast-check", json={"url": url}, headers=headers)

        if not res.ok:
            raise RuntimeError(f"[fast_check] Request failed: {res.status_code} - {res.text}")

        return res.json()