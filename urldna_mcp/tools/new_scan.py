import time
import requests
import config
from utils import get_api_key, truncate_scan_length, normalize_url

# MCP
from fastmcp.server import FastMCP


def register_new_scan(mcp: FastMCP):

    @mcp.tool(name="new_scan", title="New Scan")
    def new_scan(url: str):
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

        # Submit new scan
        try:
            response = requests.post(
                f"{config.urlDNA_API_URL}/scan",
                json={"submitted_url": url},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"[new_scan] Scan submission failed: {e}")

        scan = response.json()
        scan_id = scan.get("id")
        if not scan_id:
            raise RuntimeError("[new_scan] No scan ID returned from submission.")

        # Polling for scan completion
        status = scan.get("scan", {}).get("status", "PENDING")
        scan_result = None
        retries = 0
        max_retries = 30

        while status not in {"DONE", "ERROR"} and retries < max_retries:
            time.sleep(2)
            retries += 1
            try:
                res = requests.get(
                    f"{config.urlDNA_API_URL}/scan/{scan_id}",
                    headers=headers,
                    timeout=10
                )
                res.raise_for_status()
                scan_result = res.json()
                status = scan_result.get("scan", {}).get("status", "UNKNOWN")
            except requests.RequestException as e:
                raise RuntimeError(f"[new_scan] Failed to fetch scan status: {e}")

        if status != "DONE":
            raise RuntimeError(f"[new_scan] Scan did not complete successfully (status: {status})")

        return truncate_scan_length(scan_result)