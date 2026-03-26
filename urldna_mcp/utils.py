import os
from urllib.parse import urlparse
from fastmcp.server.dependencies import get_http_headers

def get_api_key():
    """
    Get urlDNA API Key from multiple sources in priority order:
    1. x-api-key environment variable (Claude Desktop stdio transport)
    2. URLDNA_API_KEY environment variable (local runs)
    3. x-api-key HTTP header (MCP server with SSE transport)
    """
    # Try environment variables first (works with stdio transport)
    api_key = os.getenv("x-api-key") or os.getenv("URLDNA_API_KEY")
    if api_key:
        return api_key.strip()
    
    # Try HTTP headers (works with SSE transport)
    try:
        headers = get_http_headers()
        api_key = headers.get("x-api-key")    
        if api_key:
            return api_key.replace("Bearer", "").strip()
    except Exception:
        # Headers not available, continue to error
        pass
    
    raise ValueError(
        "Missing urlDNA API key. Set via:\n"
        "  - Environment variable: x-api-key or URLDNA_API_KEY\n"
        "  - HTTP header: X-API-KEY (for SSE transport)"
    )

def normalize_url(url: str) -> str:
    """
    Ensure the URL has a valid scheme. Appends 'https://' if missing.
    """
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    return url



def _strip_blob_urls(scan: dict) -> dict:
    """
    Remove blob_url fields from screenshot and favicon sections to reduce payload size.
    """
    for field in ("screenshot", "favicon"):
        section = scan.get(field)
        if isinstance(section, dict) and "blob_url" in section:
            section.pop("blob_url")
    return scan


def truncate_scan_length(scan_result: dict) -> dict:
    """
    Reduce the scan result size to fit within the model's context window.

    Args:
        scan_result (dict): Raw urlDNA scan result JSON.
    Returns:
        dict: Cleaned and optionally truncated scan result.
    """
    if scan_result:
        # Simplify Certificate
        if scan_result.get("certificate"):
            for key in ["authority_info_access", "authority_key_identifier", "ct_precert_scts", "subject_key_identifier"]:
                scan_result["certificate"].pop(key, None)

        # Remove blob URI
        if scan_result.get("screenshot"):
            scan_result["screenshot"].pop("blob_uri", None)
        
        # Remove blob URI
        if scan_result.get("favicon"):
            scan_result["favicon"].pop("blob_uri", None)

        # Truncate Page Text (The biggest token eater)
        if scan_result.get("page") and scan_result.get("page", {}).get("text"):
            # Keep just the beginning and end to see structure/content
            full_text = scan_result["page"]["text"].strip()
            if len(full_text) > 4000:
                scan_result["page"]["text"] = full_text[:3500] + "\n[...] [TRUNCATED] [...]\n" + full_text[-500:]
        
        # Simplify Cookies
        if scan_result.get("cookies"):
            scan_result["cookies"] = [{"name": c["name"], "domain": c.get("domain")} for c in scan_result["cookies"]]
        
        # remove DOM
        if scan_result.get("dom"):
            del scan_result["dom"]
        
        # HTTP Transactions
        http_transactions = []
        for http_transaction in scan_result["http_transactions"]:
            http_transactions.append(http_transaction["url"])
        scan_result["http_trnasction"] = http_transaction

    return scan_result
        