import time
import requests
import config
from utils import get_api_key, truncate_scan_length

def register_new_scan(mcp):
    @mcp.tool()
    def new_scan(url: str):
        """
        Submit a URL to urlDNA and wait for the scan result.

        Args:
            url (str): URL to submit for scanning.
        Returns:
            dict: Truncated scan result JSON.
        Raises:
            RuntimeError: If submission or polling fails.
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
