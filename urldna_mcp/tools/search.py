import httpx
from typing import Optional

import config
from utils import get_api_key


def register_search(mcp):

    @mcp.tool(name="search", title="Search")
    async def search(query: str, page: Optional[int] = 1):
        """
        Search urlDNA scans using CQL (Custom Query Language) syntax.

        Returns matching scans sorted by submission date descending (newest first).
        Page 1 is available to all users. Pages beyond the first require a PREMIUM subscription.

        --- SEARCHABLE FIELDS ---

        id               : Scan ID (e.g., 660d0...)
        domain           : Scan domain name (e.g., "google.com")
        submitted_url    : Submitted URL for the scan (e.g., "https://www.google.com/search")
        target_url       : Final redirected URL after following all redirects
        redirect_url     : Redirect chain URL
        nsfw             : Flag for adult content (true/false)
        device           : Device used for the scan (MOBILE/DESKTOP)
        user_agent       : Web browser user agent string
        http_referer     : URL of the page that made the request
        scanned_from     : Country from which the scan was initiated
        submitter_tag    : User-defined submitter tags
        origin           : Source of the scan (USER/API)
        protocol         : Protocol used (HTTP/HTTPS)
        title            : Page title
        text             : Full page text (PREMIUM users only)
        ip               : IP address used to access the website
        org              : Organization associated with the IP
        isp              : Internet Service Provider for the IP
        asn              : Autonomous System Number associated with the IP
        city             : City associated with the IP
        country_code     : Country code associated with the IP (e.g., "IT", "US")
        http_transaction : HTTP transaction URL
        outgoing_link    : Page outgoing link
        favicon          : Perceptual hash of the website's favicon image
        screenshot       : Hash of the website's screenshot
        registrar        : Whois registrar attribute
        serial_number    : Certificate serial number (for SSL certificates)
        issuer           : Certificate issuer (for SSL certificates)
        subject          : Certificate subject (for SSL certificates)
        malicious        : Flag for malicious website (true/false)
        threat           : Detected threat classification
        technology       : Technologies used by the website
        cookie_name      : Name of a specific cookie found on the website
        cookie_value     : Value of a specific cookie found on the website
        category         : Page category (e.g., "Security") (PREMIUM users only)
        language         : Detected page language (e.g., "English") (PREMIUM users only)
        topic            : Page topics (e.g., "phishing detection") (PREMIUM users only)

        --- OPERATORS ---

        =      Exact match            → domain = google.com
        !=     Exclude exact value    → domain != facebook.com
        LIKE   Partial/wildcard match → title LIKE Login
        !LIKE  Exclude pattern        → domain !LIKE amazon

        Combine multiple filters using AND:
            domain = www.google.com AND title LIKE search

        --- EXAMPLES ---

        Find scans from mobile devices in Italy:
            query="device = MOBILE AND country_code = IT"

        Find malicious scans using WordPress:
            query="malicious = true AND technology LIKE wordpress"

        Find scans matching a specific favicon hash:
            query="favicon LIKE d417e43"

        Find scans with a specific domain and page title pattern:
            query="domain = www.google.com AND title LIKE search"

        Find non-NSFW scans submitted via API from Germany:
            query="nsfw = false AND origin = API AND country_code = DE"

        Get second page of results (PREMIUM only):
            search(query="malicious = true", page=2)

        Args:
            query (str): Search expression in urlDNA CQL syntax.
                         Combine multiple conditions with AND.
            page (int, optional): Page number for pagination (1-indexed). Default is 1.
                                  Pages beyond page 1 require a PREMIUM subscription.
        Returns:
            list[dict]: Array of Scan objects matching the query, sorted by submission date
                        descending. Each scan includes submitted_url, domain, status, device,
                        malicious flag, country, and more.
        Raises:
            RuntimeError: If the search request fails or the API key is missing.
        """
        try:
            urlDNA_api_key = get_api_key()
        except Exception as e:
            raise RuntimeError(f"[search] Failed to retrieve API key: {e}")

        headers = {
            "Authorization": urlDNA_api_key,
            "Content-Type": "application/json",
            "User-Agent": "urlDNA-MCP"
        }

        payload = {"query": query}
        params = {"page": page}
        url = f"{config.urlDNA_API_URL}/search"

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(url, json=payload, params=params, headers=headers, timeout=30.0)
                res.raise_for_status()

                return res.json()
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"[search] Request failed: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                raise RuntimeError(f"[search] Network error: {e}")