# urlDNA MCP Server

[Blog](https://urldna.io/blog/introducing-the-urldna-mcp-server-native-threat-intelligence-for-llm-agents)

![Claude Prompt](https://github.com/urldna/mcp/blob/main/claude_prompt.png?raw=true)

The `urlDNA MCP Server` enables native tool use for security-focused LLM agents like OpenAI GPT-4.1 and Claude Desktop, providing a direct interface to interact with the [urlDNA](https://urldna.io) threat intelligence platform via API.

The repository exposes the same toolset over two transports:

- `stdio` for local desktop integrations such as Claude Desktop.
- `streamable-http` for hosted deployments such as Cloud Run.

---

## Installation & Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

### Prerequisites

Install uv if you haven't already:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Quick Start

1. **Clone and setup the project:**

```bash
git clone <repository-url>
cd urlDNA-mcp-server
uv sync
```

2. **Run the MCP server locally (stdio mode):**

```bash
uv run python urldna_mcp/run.py
```

3. **Run the MCP server in streamable HTTP mode:**

```bash
uv run python urldna_mcp/server.py
```

The hosted server reads these environment variables:

- `PORT`: HTTP port to bind to. Defaults to `8080`.
- `MCP_PATH`: Public MCP endpoint path. Defaults to `/`.

### Development

```bash
# Install development dependencies
uv sync --dev

# Run tests (when available)
uv run pytest

# Format code
uv run black .

# Type checking
uv run mypy .

# Lint code
uv run flake8 .
```

---

## Hosted MCP Server

The `urlDNA MCP` server is already **hosted and available** at:

```
https://mcp.urldna.io/
```

This server is accessible over **streamable HTTP**, which makes it suitable for Cloud Run and other request-driven platforms.

You can use it directly with any platform or LLM that supports the MCP specification (e.g., Claude Desktop, OpenAI GPT-4.1).

---

## Supported Tools

### Scanning

| Tool         | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| `fast_check` | Instantly check if a URL has been scanned. Returns SAFE / MALICIOUS / UNRATED. |
| `new_scan`   | Submit a URL for a full scan and wait for the result (~30–60s).             |
| `get_scan`   | Retrieve a complete scan result by ID.                                      |

### Search

| Tool     | Description                                                                                       |
|----------|---------------------------------------------------------------------------------------------------|
| `search` | Search scans using CQL (Custom Query Language) across domain, IP, technology, malicious flag, and more. Supports `AND` and `OR` expressions plus pagination (page 2+ requires PREMIUM). |

### Saved Queries

| Tool                  | Description                                                              |
|-----------------------|--------------------------------------------------------------------------|
| `list_queries`        | List all saved queries for the authenticated user.                       |
| `get_query`           | Retrieve a specific saved query and its filters by ID.                   |
| `create_query`        | Create a new saved query with one or more CQL filter conditions.         |
| `update_query`        | Update an existing query's name and filters (full replacement).          |
| `delete_query`        | Permanently delete a saved query by ID.                                  |
| `query_scans`         | Retrieve all matching scans for a saved query.                           |

### Brand Monitoring

| Tool              | Description                                                                                      |
|-------------------|--------------------------------------------------------------------------------------------------|
| `list_brands`     | List available brands with optional name search and visibility filter (ALL / FREE / PREMIUM / USER_BRANDS). |
| `get_brand`       | Retrieve full details of a specific brand by ID.                                                 |
| `brand_scans`     | Get all scans associated with a brand. Supports additional CQL filtering.                        |

### API Reference

| Tool           | Description                                                              |
|----------------|--------------------------------------------------------------------------|
| `search_docs`  | Fetch the full urlDNA OpenAPI  and documentations.                       |

---

## Integration with Claude Desktop

To integrate the `urlDNA MCP server` in Claude Desktop, update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "urlDNA": {
      "command": "uv",
      "args": [
        "--directory",
        "<YOUR_PATH>\\mcp",
        "run",
        "urldna_mcp\\run.py"
      ],
      "env": {
        "x-api-key": "<urlDNA_API_KEY>"
      }
    }
  }
}
```

> Replace `<YOUR_PATH>` with the parent directory that contains this repository and `<urlDNA_API_KEY>` with your API key from [https://urldna.io](https://urldna.io).

For hosted MCP clients, point them at `https://mcp.urldna.io/` or your own deployed `MCP_PATH`.

Once configured, you can prompt Claude with natural language, for example:

> **"Search in urlDNA for malicious scans with title like paypal"**

> **"Create a saved query for mobile scans from Italy that are flagged as malicious"**

> **"Show me all scans associated with the Google brand"**

Claude will automatically call the correct tool and return results from the urlDNA platform.

---

## Using the MCP Server with OpenAI GPT-4.1

```python
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
          "content": [{"type": "input_text", "text": "Search in urlDNA for malicious scans with title like paypal or login"}]
        }
    ],
    text={"format": {"type": "text"}},
    reasoning={},
    tools=[
        {
            "type": "mcp",
            "server_label": "urlDNA",
            "server_url": "https://mcp.urldna.io/",
            "headers": {
                "x-api-key": "<URLDNA_API_KEY>"  # Replace with your urlDNA API key
            },
            "allowed_tools": [
                # --- Scanning ---
                "new_scan",       # Submit a URL for a full scan and wait for the result
                "get_scan",       # Retrieve a scan result by ID
                "fast_check",     # Lightweight instant safety check (SAFE / MALICIOUS / UNRATED)

                # --- Search ---
                "search",         # Search scans using CQL (Custom Query Language, AND/OR supported)

                # --- Saved Queries (PREMIUM) ---
                "list_queries",
                "get_query",
                "create_query",
                "update_query",
                "delete_query",
                "query_scans",

                # --- Brand Monitoring (PREMIUM) ---
                "list_brands",
                "get_brand",
                "brand_scans",

                # --- API Reference ---
                "search_docs",
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
```

---

## Container Deployment

Build and run with Docker:

```bash
# Build the container
docker build -t urldna-mcp-server .

# Run the server
docker run -p 8080:8080 -e x-api-key=<URLDNA_API_KEY> urldna-mcp-server

# Optional: override the public MCP path if you do not want /
docker run -p 8080:8080 -e MCP_PATH=/custom-path -e x-api-key=<URLDNA_API_KEY> urldna-mcp-server

# Cloud Run example
gcloud run deploy urldna-mcp-server \
  --source . \
  --allow-unauthenticated \
  --set-env-vars MCP_PATH=/
```

## Search Syntax

The `search` and `brand_scans` tools forward the provided CQL directly to the urlDNA API. You can combine conditions with either `AND` or `OR`.

Examples:

```text
malicious = true AND technology LIKE wordpress
domain = google.com OR domain = youtube.com
(domain = paypal.com OR title LIKE paypal) AND country_code = IT
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `uv sync --dev`
4. Make your changes and ensure tests pass
5. Format code: `uv run black .`
6. Submit a pull request

---

## Contact & Support

For support or API access, visit [https://urldna.io](https://urldna.io) or email urldna@urldna.io.