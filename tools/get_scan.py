import requests
import config
from utils import get_api_key, truncate_scan_length


def register_get_scan(mcp):

    @mcp.tool()
    def get_scan(scan_id: str):
        """
        Get scan results from urlDNA using the scan ID.

        Args:
            scan_id (str): The unique identifier of the scan.
        Returns:
            dict: Truncated scan result JSON.
        Raises:
            RuntimeError: If fetch scan fails.
        """
        # Get urlDNA API key 
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[new_scan] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json"
        }

        url = f"{config.urlDNA_API_URL}/scan/{scan_id}"
        res = requests.get(url, headers=headers)

        if not res.ok:
            raise RuntimeError(f"[get_scan] Request failed: {res.status_code} - {res.text}")

        scan_result = res.json() 

        return truncate_scan_length(scan_result)
