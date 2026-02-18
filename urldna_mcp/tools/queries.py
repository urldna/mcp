import requests
import config
from utils import get_api_key
from typing import Optional

# Valid attributes for QueryFilter
VALID_ATTRIBUTES = ["id","domain", "ip", "submitted_url", "target_url", "scanned_from", "user_agent", "nsfw", "device",
                       "origin", "asn", "org", "protocol", "title", "city", "country_code", "isp", "favicon",
                       "screenshot", "issuer", "serial_number", "subject", "malicious", "technology", "cookie_name", "http_referer"
                       "cookie_value", "http_transaction", "outgoing_link", "submitter_tag", "registrar", "category", "topic", "language", "text", "redirect_url"]

VALID_OPERATORS = ["=", "!=", "LIKE", "!LIKE"]


def _validate_filters(query_filters: list):
    """Validate that each filter has required fields and valid values."""
    for i, f in enumerate(query_filters):
        if not isinstance(f, dict):
            raise ValueError(f"Filter at index {i} must be a dict.")
        for field in ("attribute", "operator", "value"):
            if field not in f:
                raise ValueError(f"Filter at index {i} is missing required field '{field}'.")
        if f["attribute"] not in VALID_ATTRIBUTES:
            raise ValueError(
                f"Filter at index {i} has invalid attribute '{f['attribute']}'. "
                f"Valid attributes: {', '.join(VALID_ATTRIBUTES)}"
            )
        if f["operator"] not in VALID_OPERATORS:
            raise ValueError(
                f"Filter at index {i} has invalid operator '{f['operator']}'. "
                f"Valid operators: {', '.join(VALID_OPERATORS)}"
            )


def register_queries(mcp):

    @mcp.tool(name="list_queries", title="List Queries")
    def list_queries():
        """
        List all saved queries for the authenticated user.

        Saved queries are reusable filter combinations that can be executed against the
        urlDNA scan database. Each query has a name, a unique ID, and one or more filter
        conditions that are combined with logical AND.

        Use this to discover existing queries before creating new ones or to retrieve
        query IDs needed for get_query, query_scans, update_query, or delete_query.

        Returns:
            list[dict]: Array of Query objects, each containing:
                - id (str): Unique query identifier.
                - name (str): User-defined name.
                - query_filters (list): Array of filter conditions (attribute, operator, value).
        Raises:
            RuntimeError: If the API key retrieval or HTTP request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[list_queries] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.get(f"{config.urlDNA_API_URL}/queries", headers=headers)
        if not res.ok:
            raise RuntimeError(f"[list_queries] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool(name="get_query", title="get query")
    def get_query(query_id: str):
        """
        Retrieve the full details of a specific saved query by its ID.

        Returns the query name and all filter conditions configured for it.
        Use list_queries first if you don't know the query ID.

        Args:
            query_id (str): Unique identifier of the saved query (e.g., "abc123...").
        Returns:
            dict: A Query object containing:
                - id (str): Unique query identifier.
                - name (str): User-defined name.
                - query_filters (list): Array of filter conditions, each with:
                    - attribute (str): The scan attribute to filter on.
                    - operator (str): Comparison operator (=, !=, LIKE, !LIKE).
                    - value (str): The value to match against.
        Raises:
            RuntimeError: If the query ID is not found or the request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[get_query] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.get(f"{config.urlDNA_API_URL}/query/{query_id}", headers=headers)
        if not res.ok:
            raise RuntimeError(f"[get_query] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool(name="query_scans", title="Query Scans")
    def query_scans(query_id: str, page: Optional[int] = 1):
        """
        Execute a saved query and return all matching scans.

        Runs all filter conditions stored in the query against the urlDNA database
        and returns matching scans sorted by submission date (newest first).
        Pages beyond the first require a PREMIUM subscription.

        Args:
            query_id (str): Unique identifier of the saved query to execute.
            page (int, optional): Page number for pagination (1-indexed). Default is 1.
                                  Pages > 1 require PREMIUM subscription.
        Returns:
            list[dict]: Array of Scan objects matching the query filters, sorted by
                        submission date descending. Each scan includes metadata such as
                        submitted_url, domain, status, device, malicious flag, etc.
        Raises:
            RuntimeError: If the query ID is not found or the request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[query_scans] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.get(
            f"{config.urlDNA_API_URL}/query/{query_id}/scans",
            params={"page": page},
            headers=headers
        )
        if not res.ok:
            raise RuntimeError(f"[query_scans] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool(name="create_query", title="Create Query")
    def create_query(name: str, query_filters: list):
        """
        Create a new saved query with one or more filter conditions.

        Saved queries allow reusable, complex searches across the urlDNA database.
        All filter conditions are combined with logical AND. Requires PREMIUM subscription.

        --- QUERY FILTER STRUCTURE ---
        Each filter in query_filters must be a dict with:
            - attribute (str): The scan attribute to filter on.
            - operator  (str): Comparison operator.
            - value     (str): The value to match.

        --- VALID ATTRIBUTES ---
        id, domain, ip, submitted_url, target_url, scanned_from, user_agent, nsfw,
        device, origin, asn, org, protocol, title, city, country_code, isp, favicon,
        screenshot, issuer, serial_number, subject, malicious, technology, cookie_name,
        http_referer, cookie_value, http_transaction, outgoing_link, submitter_tag,
        registrar, category, topic, language, text, redirect_url, threat

        --- VALID OPERATORS ---
        =      Exact match             (e.g., malicious = true)
        !=     Exclude exact value     (e.g., device != MOBILE)
        LIKE   Partial/wildcard match  (e.g., technology LIKE wordpress)
        !LIKE  Exclude pattern         (e.g., domain !LIKE amazon)

        --- EXAMPLES ---
        Find malicious mobile scans from Italy:
            query_filters = [
                {"attribute": "malicious", "operator": "=",    "value": "true"},
                {"attribute": "device",    "operator": "=",    "value": "MOBILE"},
                {"attribute": "country_code", "operator": "=", "value": "IT"}
            ]

        Find scans using WordPress, not from Facebook:
            query_filters = [
                {"attribute": "technology", "operator": "LIKE", "value": "wordpress"},
                {"attribute": "domain",     "operator": "!=",   "value": "facebook.com"}
            ]

        Args:
            name (str): Descriptive name for the saved query (e.g., "Malicious IT Mobile Scans").
            query_filters (list[dict]): Array of filter conditions. Each dict requires:
                - attribute (str): Scan field to filter on (see valid attributes above).
                - operator  (str): One of =, !=, LIKE, !LIKE.
                - value     (str): Value to match against the attribute.
        Returns:
            list[dict]: Array of all user Query objects after creation.
        Raises:
            ValueError: If any filter is missing required fields or contains invalid values.
            RuntimeError: If the API key retrieval or HTTP request fails.
        """
        _validate_filters(query_filters)

        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[create_query] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        payload = {"name": name, "query_filters": query_filters}
        res = requests.post(f"{config.urlDNA_API_URL}/query", json=payload, headers=headers)
        if not res.ok:
            raise RuntimeError(f"[create_query] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool(name="update_query", title="Update Query")
    def update_query(query_id: str, name: str, query_filters: list):
        """
        Update an existing saved query's name and/or filter conditions.

        Replaces ALL previous filter conditions with the new provided list.
        Partial updates are not supported — always provide the full desired filter set.
        Requires PREMIUM subscription.

        --- QUERY FILTER STRUCTURE ---
        Each filter in query_filters must be a dict with:
            - attribute (str): The scan attribute to filter on.
            - operator  (str): Comparison operator.
            - value     (str): The value to match.

        --- VALID ATTRIBUTES ---
        id, domain, ip, submitted_url, target_url, scanned_from, user_agent, nsfw,
        device, origin, asn, org, protocol, title, city, country_code, isp, favicon,
        screenshot, issuer, serial_number, subject, malicious, technology, cookie_name,
        http_referer, cookie_value, http_transaction, outgoing_link, submitter_tag,
        registrar, category, topic, language, text, redirect_url, threat

        --- VALID OPERATORS ---
        =      Exact match             (e.g., malicious = true)
        !=     Exclude exact value     (e.g., device != MOBILE)
        LIKE   Partial/wildcard match  (e.g., technology LIKE wordpress)
        !LIKE  Exclude pattern         (e.g., domain !LIKE amazon)

        Args:
            query_id (str): Unique identifier of the query to update.
            name (str): New name for the query.
            query_filters (list[dict]): Full replacement filter list. Each dict requires:
                - attribute (str): Scan field to filter on.
                - operator  (str): One of =, !=, LIKE, !LIKE.
                - value     (str): Value to match against the attribute.
        Returns:
            dict: The updated Query object.
        Raises:
            ValueError: If any filter is missing required fields or contains invalid values.
            RuntimeError: If the query ID is not found or the request fails.
        """
        _validate_filters(query_filters)

        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[update_query] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        payload = {"name": name, "query_filters": query_filters}
        res = requests.put(f"{config.urlDNA_API_URL}/query/{query_id}", json=payload, headers=headers)
        if not res.ok:
            raise RuntimeError(f"[update_query] Request failed: {res.status_code} - {res.text}")

        return res.json()

    @mcp.tool(name="delete_query", title="Delete Query")
    def delete_query(query_id: str):
        """
        Permanently delete a saved query by its ID.

        This operation is irreversible — the query and all its filter conditions
        are permanently removed. The scans matched by the query are not affected.

        Use list_queries to confirm the query ID before deleting.

        Args:
            query_id (str): Unique identifier of the query to delete.
        Returns:
            dict: Confirmation response from the API.
        Raises:
            RuntimeError: If the query ID is not found or the request fails.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[delete_query] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        res = requests.delete(f"{config.urlDNA_API_URL}/query/{query_id}", headers=headers)
        if not res.ok:
            raise RuntimeError(f"[delete_query] Request failed: {res.status_code} - {res.text}")

        return res.json() if res.text else {"status": "deleted", "query_id": query_id}