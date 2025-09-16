# urlDNA MCP Server
[Blog](https://medium.com/@urldna/introducing-the-urldna-mcp-server-native-threat-intelligence-for-llm-agents-6330a35dcf05)

![Claude Prompt](https://github.com/urldna/mcp/blob/main/claude_prompt.png?raw=true)

The `urlDNA MCP Server` enables native tool use for security-focused LLM agents like OpenAI GPT-4.1 and Claude 3 Desktop, providing a direct interface to interact with the [urlDNA](https://urldna.io) threat intelligence platform via API.

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

3. **Run the MCP server in SSE mode:**
```bash
uv run python urldna_mcp/server.py
```

### Development

To work on the project:

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
https://mcp.urldna.io/sse
```

This server is accessible over **Server-Sent Events (SSE)** protocol, which supports streaming interactions between LLMs and the backend tools.

You can use it directly with any platform or LLM supporting the `mcp` specification (e.g., Claude Desktop, OpenAI GPT-4.1).

---

## Supported Actions

The following tools are exposed by the MCP interface:

| Tool         | Description                                                    |
|--------------|----------------------------------------------------------------|
| `new_scan`   | Submit a new scan for a given URL                              |
| `get_scan`   | Retrieve a scan by ID                                          |
| `search`     | Search scans using text, domain, or filters                    |
| `fast_check` | Lightweight phishing detection via content + redirect analysis |

---

## Integration with Claude Desktop (Anthropic MCP)

To integrate the `urlDNA MCP server` in Claude Desktop, update your Claude configuration (typically `claude.config.json` or equivalent) like so:

```json
{
  "mcpServers": {
    "urlDNA": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "<YOUR_PATH>/urldna_mcp/run.py"
      ],
      "env": {
        "authorization": "<urlDNA_API_KEY>"
      }
    }
  }
}
```

> Replace `<YOUR_PATH>` with the actual path to the project directory, and `<urlDNA_API_KEY>` with your API key from [https://urldna.io](https://urldna.io).

Once configured, you can prompt Claude with natural language requests like:

> **"Search in urlDNA for malicious scans with title like paypal"**

Claude will automatically call the correct tool and return results from the `urlDNA` platform.

---

## Using the MCP Server with OpenAI GPT-4.1 (Python SDK)

```python
from openai import OpenAI

# Initialize OpenAI client (assumes API key is set via env var or config)
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "system",
            "content": [{"type": "input_text", "text": "You are a cybersecurity analyst using urlDNA."}]
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Search in urlDNA malicious scan with title like paypal"}]
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
                "Authorization": "Bearer <URLDNA_API_KEY>"
            },
            "allowed_tools": ["new_scan", "get_scan", "search", "fast_check"],
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

## Container Deployment

Build and run with Docker:

```bash
# Build the container
docker build -t urldna-mcp-server .

# Run the server
docker run -p 8080:8080 -e authorization=<URLDNA_API_KEY> urldna-mcp-server
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

---