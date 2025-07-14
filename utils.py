import os
import json
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


def get_max_context_length():
    """
    Get max context length from HTTP headers or os environment.
    Header key: "contentx-length"
    """
    headers = get_http_headers()
    context_length = headers.get("contentx-length")
    if context_length is None:
        context_length = os.getenv("contentx-length")
    try:
        return int(context_length)
    except (ValueError, TypeError):
        return 0


def truncate_scan_length(scan_result):
    """
    Truncate scan result JSON if it exceeds max context length.
    Attributes are removed in the following order until the size is within limit:
    1. "dom"
    2. "http_transactions"
    3. "page.text"
    
    :param scan_result: dict - urlDNA Scan Result JSON
    :return: dict - truncated scan result
    """
    context_length = get_max_context_length()

    # Work on a copy to avoid mutating the original input
    truncated = dict(scan_result)
    
    # If context length not provided remove dom anyway
    if context_length <= 0:
        if "dom" in truncated:
            del truncated["dom"]

    # Helper to calculate JSON size in characters
    def json_length(obj):
        return len(json.dumps(obj, separators=(',', ':')))

    # If already under the limit, return as-is
    if json_length(truncated) <= context_length:
        return truncated

    # Truncate in the specified order
    drop_order = [
        ("dom",),
        ("http_transactions",),
        ("page", "text")
    ]

    for path in drop_order:
        obj = truncated
        *parents, last = path

        # Navigate to the parent
        for key in parents:
            obj = obj.get(key, {})
            if not isinstance(obj, dict):
                break
        else:
            # Only attempt to remove if the key exists
            if last in obj:
                obj.pop(last)
                if json_length(truncated) <= context_length:
                    break

    return truncated
