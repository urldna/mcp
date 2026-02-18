import requests
import config
from utils import get_api_key, truncate_scan_length


def register_get_scan(mcp):

    @mcp.tool()
    def get_scan(scan_id: str):
        """
        Retrieve the full results of a previously submitted urlDNA scan by its ID.

        Use this tool when you already have a scan ID (e.g., from new_scan or search results)
        and want to fetch the detailed scan report. 

        Args:
            scan_id (str): The unique identifier of the scan (e.g., "660d0abc123...").
                           Obtained from new_scan, fast_check, or search results.
        Returns:
            dict: Truncated scan result JSON including page metadata, threat classification,
                  technologies, certificates, network info, and more.
        Raises:
            RuntimeError: If API key retrieval or the HTTP request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[get_scan] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        url = f"{config.urlDNA_API_URL}/scan/{scan_id}"
        res = requests.get(url, headers=headers)

        if not res.ok:
            raise RuntimeError(f"[get_scan] Request failed: {res.status_code} - {res.text}")

        scan_result = res.json()

        return truncate_scan_length(scan_result)