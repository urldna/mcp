from openai import OpenAI

# Initialize OpenAI client (assumes OPENAI_API_KEY is set via environment variable)
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",  # GPT-4.1 supports native MCP tool use
    input=[
        {
            "role": "system",
            "content": [{"type": "input_text", "text": "You are a cybersecurity analyst using urlDNA."}]
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Search in urlDNA for malicious scans with title like paypal"}]
        }
    ],
    text={"format": {"type": "text"}},
    reasoning={},
    tools=[
        {
            "type": "mcp",
            "server_label": "urlDNA",
            "server_url": "https://mcp.urldna.io/sse",
            "headers": {
                "Authorization": "Bearer <URLDNA_API_KEY>"  # Replace with your urlDNA API key
            },
            "allowed_tools": [
                # --- Scanning ---
                "new_scan",       # Submit a URL for a full scan and wait for the result
                "get_scan",       # Retrieve a scan result by ID
                "fast_check",     # Lightweight instant safety check (SAFE / MALICIOUS / UNRATED)

                # --- Search ---
                "search",         # Search scans using CQL (Custom Query Language)

                # --- Saved Queries (PREMIUM) ---
                "list_queries",         # List all saved queries
                "get_query",            # Get a specific saved query by ID
                "create_query",         # Create a new saved query with filter conditions
                "update_query",         # Update an existing saved query (full replacement)
                "delete_query",         # Permanently delete a saved query
                "execute_query_scans",  # Run a saved query and return matching scans

                # --- Brand Monitoring (PREMIUM) ---
                "list_brands",      # List available brands with optional name/visibility filter
                "get_brand",        # Get full details of a specific brand by ID
                "get_brand_scans",  # Get all scans associated with a brand (supports CQL filter)

                # --- API Reference ---
                "get_api_docs",     # Fetch the full urlDNA OpenAPI specification
            ],
            "require_approval": "never"
        }
    ],
    temperature=0.7,
    top_p=1,
    max_output_tokens=2048,
    store=True
)

print(response.output)