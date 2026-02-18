import os
import json
from urllib.parse import urlparse
from fastmcp.server.dependencies import get_http_headers

def get_api_key():
    """
    Get urlDNA API Key from HTTP request header or os environment.
    Header key: "authorization"
    """
    headers = get_http_headers()
    auth_header = headers.get("authorization", "")
    urlDNA_api_key = auth_header.removeprefix("Bearer").strip()
    if not urlDNA_api_key:
        urlDNA_api_key = os.getenv("authorization")
    if not urlDNA_api_key:
        raise ValueError("Missing or invalid Authorization header")
    
    return urlDNA_api_key


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
        if "certificate" in scan_result:
            for key in ["authority_info_access", "authority_key_identifier", "ct_precert_scts", "subject_key_identifier"]:
                scan_result["certificate"].pop(key, None)

        # Remove blob URI
        if "screenshot" in scan_result:
            scan_result["screenshot"].pop("blob_uri", None)
        
        # Remove blob URI
        if "favicon" in scan_result:
            scan_result["favicon"].pop("blob_uri", None)

        # Truncate Page Text (The biggest token eater)
        if "page" in scan_result and "text" in scan_result["page"]:
            # Keep just the beginning and end to see structure/content
            full_text = scan_result["page"]["text"].strip()
            if len(full_text) > 4000:
                scan_result["page"]["text"] = full_text[:3500] + "\n[...] [TRUNCATED] [...]\n" + full_text[-500:]
        
        # Simplify Cookies
        if "cookies" in scan_result:
            scan_result["cookies"] = [{"name": c["name"], "domain": c.get("domain")} for c in scan_result["cookies"]]
        
        # remove DOM
        if "dom" in scan_result:
            del scan_result["dom"]
        
        # HTTP Transactions
        http_transactions = []
        for http_transaction in scan_result["http_transactions"]:
            http_transactions.append(http_transaction["url"])
        scan_result["http_trnasction"] = http_transaction

    return scan_result
        