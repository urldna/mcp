
import config
import requests
from utils import get_api_key


def register_search(mcp):

    @mcp.tool()
    def search(query: str):
        """
        Search scans using urlDNA custom search syntax.

        Searchable fields include: domain, ip, submitted_url, target_url, device, country_code, title, technology, favicon, malicious, and many more.

        Operators supported: =, !=, LIKE, !LIKE, >, >=, <, <=

        Examples:
            - domain = www.google.com AND title LIKE search
            - device = MOBILE AND country_code = IT
            - malicious = false AND technology LIKE wordpress

        Args:
            query (str): Query in urlDNA CQL syntax.
        Returns:
            dict: List of scan.
        Raises:
            RuntimeError: If ssearch fails.
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

        # Perform the search request
        res = requests.post(
            f"{config.urlDNA_API_URL}/search",
            json={"query": query},
            headers=headers
        )

        if not res.ok:
            raise RuntimeError(f"Search failed: {res.status_code} - {res.text}")

        return res.json()
