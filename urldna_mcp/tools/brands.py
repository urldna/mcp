import requests
import config
from utils import get_api_key
from typing import Optional


def register_brands(mcp):

    @mcp.tool()
    def list_brands(
        filter: Optional[str] = None,
        query: Optional[str] = None,
        page: Optional[int] = 1
    ):
        """
        List all brands available to the authenticated user for threat monitoring.

        Brands represent organizations or entities whose domains and assets are tracked
        in the urlDNA database. Use brands to monitor phishing attempts, brand impersonation,
        and suspicious lookalike domains. Requires PREMIUM subscription.

        --- FILTER OPTIONS ---
        ALL         : All brands accessible to the user (default if omitted).
        FREE        : Public brands available to all users.
        PREMIUM     : Premium-tier brands with advanced monitoring.
        USER_BRANDS : Brands created by the authenticated user.

        --- EXAMPLES ---
        List all brands:
            list_brands()

        Search for brands containing "google":
            list_brands(query="google")

        List only user-created brands:
            list_brands(filter="USER_BRANDS")

        Search public brands with pagination:
            list_brands(filter="FREE", query="microsoft", page=2)

        Args:
            filter (str, optional): Visibility filter for brands.
                One of: ALL, FREE, PREMIUM, USER_BRANDS. Default: returns all accessible brands.
            query (str, optional): Search term for filtering brands by name (case-insensitive partial match).
                                   Example: "google" will match "Google LLC", "Google Cloud", etc.
            page (int, optional): Page number for pagination (1-indexed). Default is 1.
                                  Pages > 1 require PREMIUM subscription.
        Returns:
            list[dict]: Array of Brand objects, each containing:
                - id (str): Unique brand identifier.
                - name (str): Brand name.
                - private_brand (bool): True if only visible to the creating user.
        Raises:
            ValueError: If an invalid filter value is provided.
            RuntimeError: If the API key retrieval or HTTP request fails.
        """
        valid_filters = {"ALL", "FREE", "PREMIUM", "USER_BRANDS"}
        if filter is not None and filter not in valid_filters:
            raise ValueError(
                f"[list_brands] Invalid filter '{filter}'. "
                f"Valid options: {', '.join(sorted(valid_filters))}"
            )

        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[list_brands] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        params = {"page": page}
        if filter is not None:
            params["filter"] = filter
        if query is not None:
            params["query"] = query

        res = requests.get(f"{config.urlDNA_API_URL}/brands", params=params, headers=headers)
        if not res.ok:
            raise RuntimeError(f"[list_brands] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool()
    def get_brand(brand_id: str):
        """
        Retrieve the full details of a specific brand by its ID.

        Returns complete brand metadata including configuration and visibility settings.
        Use list_brands first if you need to look up a brand ID by name.
        Requires PREMIUM subscription.

        Args:
            brand_id (str): Unique identifier of the brand (e.g., "abc123...").
                            Obtain from list_brands.
        Returns:
            dict: A Brand object containing:
                - id (str): Unique brand identifier.
                - name (str): Brand name.
                - private_brand (bool): True if only visible to the creating user.
        Raises:
            RuntimeError: If the brand ID is not found or the request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[get_brand] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.get(f"{config.urlDNA_API_URL}/brand/{brand_id}", headers=headers)
        if not res.ok:
            raise RuntimeError(f"[get_brand] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool()
    def get_brand_scans(
        brand_id: str,
        query: Optional[str] = None,
        page: Optional[int] = 1
    ):
        """
        Retrieve all scans associated with a specific brand.

        Returns scans linked to the brand, sorted by submission date (newest first).
        Optionally filter results further using CQL (Custom Query Language) syntax
        for more targeted threat analysis. Requires PREMIUM subscription.

        --- CQL FILTER SYNTAX (optional query parameter) ---
        Combine scan attributes using AND:
            malicious = true AND device = MOBILE
            country_code = IT AND technology LIKE phishing

        Supported operators: =, !=, LIKE, !LIKE

        Searchable attributes include:
            domain, ip, submitted_url, target_url, malicious, device, country_code,
            technology, title, user_agent, scanned_from, and many more.
            See the search tool docstring for the full attribute list.

        --- EXAMPLES ---
        Get all scans for a brand:
            get_brand_scans(brand_id="abc123")

        Get only malicious scans for a brand:
            get_brand_scans(brand_id="abc123", query="malicious = true")

        Get mobile scans from Italy for a brand:
            get_brand_scans(brand_id="abc123", query="device = MOBILE AND country_code = IT")

        Get second page of results:
            get_brand_scans(brand_id="abc123", page=2)

        Args:
            brand_id (str): Unique identifier of the brand to retrieve scans for.
                            Obtain from list_brands or get_brand.
            query (str, optional): Optional CQL expression for additional filtering.
                                   See POST /v1/search documentation for full CQL syntax.
            page (int, optional): Page number for pagination (1-indexed). Default is 1.
                                  Pages > 1 require PREMIUM subscription.
        Returns:
            list[dict]: Array of Scan objects associated with the brand, sorted by
                        submission date descending. Each scan includes submitted_url,
                        domain, device, malicious flag, status, country, and more.
        Raises:
            RuntimeError: If the brand ID is not found or the request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[get_brand_scans] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        params = {"page": page}
        if query is not None:
            params["query"] = query

        res = requests.get(
            f"{config.urlDNA_API_URL}/brand/{brand_id}/scans",
            params=params,
            headers=headers
        )
        if not res.ok:
            raise RuntimeError(f"[get_brand_scans] Request failed: {res.status_code} - {res.text}")

        return res.json()