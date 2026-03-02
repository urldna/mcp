import httpx
import asyncio

import config
from utils import get_api_key, truncate_scan_length, normalize_url

# MCP
from fastmcp.server import FastMCP


def register_new_scan(mcp: FastMCP):

    @mcp.tool(name="new_scan", title="New Scan")
    async def new_scan(url: str):
        """
        Submit a URL to urlDNA for a full scan and wait for the result.

        This tool performs a complete website scan: it submits the URL, then polls
        the API until the scan finishes (status: DONE) or fails (status: ERROR).
        The result is automatically truncated to fit within the model's context window.

        The URL is automatically normalized: if no scheme is provided (e.g., "example.com"),
        "https://" is prepended automatically.

        Polling behavior:
            - Checks every 2 seconds
            - Maximum 30 retries (up to ~60 seconds)
            - Raises an error if the scan does not complete in time

        Args:
            url (str): URL to submit for scanning. Can be provided with or without the "https://" prefix.
                       Examples: "https://example.com", "example.com", "www.suspicious-site.net"
        Returns:
            dict: Truncated scan result JSON from urlDNA, including page metadata,
                  technologies, HTTP transactions, threat classification, and more.
        Raises:
            RuntimeError: If submission fails, polling fails, or the scan does not complete successfully.
        """
        # Normalize URL
        url = normalize_url(url)

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

        async with httpx.AsyncClient() as client:
            # Submit Scan
            res = await client.post(f"{config.urlDNA_API_URL}/scan", json={"submitted_url": url}, headers=headers)
            res.raise_for_status()
            scan_id = res.json().get("id")

            # Poll (Asynchronously)
            status = "PENDING"
            max_retries = 60
            sleep_time = 2
            try:
                for _ in range(max_retries):
                    await asyncio.sleep(sleep_time) 
                    
                    check = await client.get(f"{config.urlDNA_API_URL}/scan/{scan_id}", headers=headers)
                    data = check.json()
                    status = data.get("scan", {}).get("status", "UNKNOWN")
                    
                    if status in {"DONE", "ERROR", "PAGE_NOT_AVAILABLE"}:
                        if status == "DONE":
                            return truncate_scan_length(data)
                        raise RuntimeError(f"[new_scan] Scan failed with status: {status}")

                raise RuntimeError(f"[new_scan] Scan timed out after {max_retries*sleep_time} seconds.")
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"[new_scan] Request failed: {e.response.status_code} - {e.response.text}")
